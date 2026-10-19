"""观测相关请求体。"""

from typing import Literal

from pydantic import BaseModel, Field


class FeedbackRequest(BaseModel):
    # 与服务层约定一致：只能是赞或踩
    rating: Literal[1, -1] = Field(description="1=点赞，-1=点踩")
    comment: str | None = Field(default=None, max_length=500, description="可选备注")


class AnswerPreviewRequest(BaseModel):
    answer: str = Field(min_length=1, max_length=20000, description="浏览器侧模型生成的回答")


class MetricsCards(BaseModel):
    """观测看板顶部指标。"""

    total_runs: int
    success_runs: int
    failed_runs: int
    cancelled_runs: int
    unfinished_runs: int
    success_rate: float
    avg_elapsed_ms: int
    up_count: int
    down_count: int
    up_rate: float


class MetricsBucket(BaseModel):
    """分布图上的一个分档（路由分布等）。"""

    name: str
    count: int


class MetricsStepStat(BaseModel):
    """按阶段聚合的耗时，用来找瓶颈。"""

    step_name: str
    count: int
    avg_ms: int
    max_ms: int


class MetricsDayPoint(BaseModel):
    """近 N 天每天的运行量。"""

    date: str
    count: int


class MetricsStats(BaseModel):
    """观测看板：指标卡片 + 路由分布 + 阶段耗时 + 运行量趋势。"""

    cards: MetricsCards
    route_distribution: list[MetricsBucket]
    step_stats: list[MetricsStepStat]
    run_trend: list[MetricsDayPoint]
    trend_days: int
