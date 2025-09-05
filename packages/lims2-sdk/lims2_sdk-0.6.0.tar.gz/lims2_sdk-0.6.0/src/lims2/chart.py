"""图表服务模块

基于原 biotree_chart 功能实现
"""

import gzip
from pathlib import Path
from typing import Any, Optional, Union

import orjson

from .network import network_retry
from .oss_base import OSSMixin
from .thumbnail import generate_thumbnail
from .utils import (
    clean_plotly_data,
    generate_unique_filename,
    get_file_size,
    handle_api_response,
    read_file_content,
    round_floats,
)


class ChartService(OSSMixin):
    """图表服务"""

    def __init__(self, client):
        """初始化图表服务

        Args:
            client: Lims2Client 实例
        """
        self.client = client
        self.config = client.config
        self.session = client.session

        # 初始化OSS混入功能
        self.__init_oss__()

    def upload(
        self,
        data_source: Union[dict[str, Any], str, Path],
        project_id: str,
        chart_name: str,
        sample_id: Optional[str] = None,
        chart_type: Optional[str] = None,
        description: Optional[str] = None,
        contrast: Optional[str] = None,
        analysis_node: Optional[str] = None,
        precision: Optional[int] = None,
        generate_thumbnail: Optional[bool] = None,
    ) -> dict[str, Any]:
        """上传图表

        Args:
            data_source: 图表数据源，可以是字典、文件路径或 Path 对象
            project_id: 项目 ID
            chart_name: 图表名称
            sample_id: 样本 ID（可选）
            chart_type: 图表类型（可选）
            description: 图表描述（可选）
            contrast: 对比策略（可选）
            analysis_node: 分析节点名称（可选）
            precision: 浮点数精度控制，保留小数位数（0-10，默认3）
            generate_thumbnail: 是否生成缩略图，None时使用配置中的auto_generate_thumbnail

        Returns:
            上传结果
        """
        # 参数验证
        if not chart_name:
            raise ValueError("图表名称不能为空")
        if not project_id:
            raise ValueError("项目 ID 不能为空")
        if not data_source:
            raise ValueError("数据源不能为空")
        if precision is not None and not 0 <= precision <= 10:
            raise ValueError("precision 必须在 0-10 之间")

        # 构建请求数据
        request_data = {
            "chart_name": chart_name,
            "project_id": project_id,
            "chart_type": chart_type,
            "description": description,
        }

        # 添加可选参数
        if sample_id:
            request_data["sample_id"] = sample_id
        if contrast:
            request_data["contrast"] = contrast
        if analysis_node:
            request_data["analysis_node"] = analysis_node

        # 根据数据源类型处理
        if isinstance(data_source, dict):
            return self._upload_from_dict(
                request_data, data_source, precision, generate_thumbnail
            )
        elif isinstance(data_source, (str, Path)):
            return self._upload_from_file(
                request_data, data_source, precision, generate_thumbnail
            )
        else:
            raise ValueError("数据源必须是字典、文件路径或 Path 对象")

    def _upload_from_dict(
        self,
        request_data: dict[str, Any],
        chart_data: dict[str, Any],
        precision: Optional[int] = None,
        generate_thumbnail: Optional[bool] = None,
    ) -> dict[str, Any]:
        """从字典数据上传图表

        关键字段说明:
        - file_name: 不带扩展名的文件名，用于服务端显示
        - file_format: 文件格式，如'json'，用于服务端验证
        - oss_key: OSS中的存储路径，包含带时间戳的唯一文件名
        """
        # 检测渲染器类型
        if "data" in chart_data and "layout" in chart_data:
            request_data["renderer_type"] = "plotly"
        elif "elements" in chart_data or (
            "nodes" in chart_data and "edges" in chart_data
        ):
            request_data["renderer_type"] = "cytoscape"
        else:
            raise ValueError("不支持的图表数据格式")

        # 应用精度控制（默认使用 3 位小数）
        if precision is None:
            precision = 3  # 默认精度为 3

        # 清理Plotly数据，移除不必要的属性
        if request_data["renderer_type"] == "plotly":
            chart_data = clean_plotly_data(chart_data)

        # 应用精度控制并序列化
        chart_data = round_floats(chart_data, precision)
        json_str = orjson.dumps(chart_data).decode("utf-8")

        # 设置文件信息
        # 从文件上传时已设置file_name，从字典上传时使用chart_name
        if "file_name" not in request_data:
            request_data["file_name"] = request_data["chart_name"]
        request_data["file_format"] = "json"

        # 压缩并上传到OSS
        compressed_data = gzip.compress(json_str.encode("utf-8"))
        filename = generate_unique_filename(
            request_data["file_name"], "json"
        )  # 用于OSS存储
        oss_key = self._build_chart_oss_key(
            request_data["project_id"], request_data.get("sample_id"), filename
        )
        bucket = self._get_oss_bucket(request_data["project_id"])

        # 上传到OSS，如果失败则直接抛出原始异常，不创建数据库记录
        self._put_object_with_retry(
            bucket,
            oss_key,
            compressed_data,
            headers={
                "Content-Type": "application/json",
                "Content-Encoding": "gzip",
            },
        )

        request_data["oss_key"] = oss_key

        # 生成缩略图
        should_generate = (
            generate_thumbnail
            if generate_thumbnail is not None
            else self.config.auto_generate_thumbnail
        )
        if should_generate and request_data.get("renderer_type") == "plotly":
            print("开始生成缩略图...")
            self._generate_and_upload_thumbnail(chart_data, request_data)

        # 创建图表记录
        return self._create_chart_record(request_data)

    def _upload_from_file(  # noqa: C901
        self,
        request_data: dict[str, Any],
        file_path: Union[str, Path],
        precision: Optional[int] = None,
        generate_thumbnail: Optional[bool] = None,
    ) -> dict[str, Any]:
        """从文件上传图表"""
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        file_format = file_path.suffix.lower().strip(".")
        request_data["file_size"] = get_file_size(file_path)

        # JSON 文件特殊处理
        if file_format == "json":
            try:
                chart_data = read_file_content(file_path)
                if isinstance(chart_data, dict):
                    # 使用原始文件名（不带扩展名）
                    request_data["file_name"] = file_path.stem
                    return self._upload_from_dict(
                        request_data, chart_data, precision, generate_thumbnail
                    )
            except FileNotFoundError:
                raise
            except orjson.JSONDecodeError as e:
                raise ValueError(f"JSON 文件格式错误: {e}")
            except Exception as e:
                raise ValueError(f"读取 JSON 文件失败: {e}")

        # 其他文件类型
        if file_format in ["png", "jpg", "jpeg", "svg", "pdf"]:
            request_data["renderer_type"] = "image"
        elif file_format == "html":
            request_data["renderer_type"] = "html"
        else:
            raise ValueError(f"不支持的文件格式: {file_format}")

        # 设置文件信息
        request_data["file_format"] = file_format
        request_data["file_name"] = file_path.stem  # 不带扩展名
        filename = generate_unique_filename(file_path.stem, file_format)  # 用于OSS存储

        # 构建OSS键名
        oss_key = self._build_chart_oss_key(
            request_data["project_id"], request_data.get("sample_id"), filename
        )

        # 读取文件内容
        file_content = read_file_content(file_path)
        if isinstance(file_content, dict):
            file_content = orjson.dumps(file_content)

        # 上传到 OSS
        content_type = self._get_content_type(file_format)
        bucket = self._get_oss_bucket(request_data["project_id"])

        # 上传到OSS，如果失败则直接抛出原始异常，不创建数据库记录
        self._put_object_with_retry(
            bucket, oss_key, file_content, headers={"Content-Type": content_type}
        )

        request_data["oss_key"] = oss_key

        # 创建图表记录
        return self._create_chart_record(request_data)

    def _build_chart_oss_key(
        self, project_id: str, sample_id: Optional[str], filename: str
    ) -> str:
        """构建图表的OSS键名

        Args:
            project_id: 项目ID
            sample_id: 样本ID（可选）
            filename: 文件名

        Returns:
            str: OSS键名，格式为biochart/{env}/project_id/[sample_id/]filename
            - 环境前缀：生产环境使用media，测试环境使用test
        """
        # 使用环境相关的路径前缀
        env_prefix = self._get_oss_path_prefix()
        parts = ["biochart", env_prefix, project_id]
        if sample_id:
            parts.append(sample_id)
        parts.append(filename)
        return "/".join(parts)

    @network_retry(max_retries=3, base_delay=1.0, max_delay=15.0)
    def _create_chart_record(self, request_data: dict[str, Any]) -> dict[str, Any]:
        """创建图表记录"""

        request_data["token"] = self.config.token
        request_data["team_id"] = self.config.team_id

        # 使用配置的超时时间和分离的连接/读取超时
        timeout = (self.config.connection_timeout, self.config.read_timeout)

        response = self.session.post(
            f"{self.config.api_url}/get_data/biochart/create_chart/",
            json=request_data,
            timeout=timeout,
        )
        return handle_api_response(response, "创建图表记录")

    def _get_content_type(self, file_format: str) -> str:
        """获取文件内容类型"""
        content_types = {
            "json": "application/json",
            "png": "image/png",
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "svg": "image/svg+xml",
            "pdf": "application/pdf",
            "html": "text/html",
        }
        return content_types.get(file_format, "application/octet-stream")

    def _generate_and_upload_thumbnail(
        self, chart_data: dict[str, Any], request_data: dict[str, Any]
    ) -> None:
        """生成并上传缩略图到OSS"""
        try:
            # 此时chart_data已经被清理过了，直接使用
            thumb_bytes = generate_thumbnail(
                chart_data,
                self.config.thumbnail_width,
                self.config.thumbnail_height,
                self.config.thumbnail_format,
            )
            if thumb_bytes:
                # file_name已经不带扩展名，直接使用
                thumb_filename = (
                    f"{request_data['file_name']}_thumb.{self.config.thumbnail_format}"
                )
                thumb_oss_key = self._build_chart_oss_key(
                    request_data["project_id"],
                    request_data.get("sample_id"),
                    thumb_filename,
                )
                bucket = self._get_oss_bucket(request_data["project_id"])
                content_type = f"image/{self.config.thumbnail_format}"

                self._put_object_with_retry(
                    bucket,
                    thumb_oss_key,
                    thumb_bytes,
                    headers={"Content-Type": content_type},
                )
                img_url = f"https://image.lims2.com/{thumb_oss_key}"
                request_data["img_url"] = img_url
                print(f"缩略图已生成: {img_url}")
        except Exception:
            pass  # 缩略图失败不影响正常上传
