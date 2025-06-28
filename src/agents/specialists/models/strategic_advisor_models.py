from pydantic import BaseModel, Field
from typing import List

class StrategicAdvice(BaseModel):
    """A Pydantic model for structured strategic real estate advice."""
    market_overview: str = Field(..., description="A summary of the current market conditions, highlighting the most relevant trends from the analysis.")
    key_opportunities: List[str] = Field(..., description="A list of specific investment opportunities, explaining why they are suitable for the client.")
    potential_risks: List[str] = Field(..., description="A list of potential risks and challenges the client should be aware of.")
    recommended_strategy: List[str] = Field(..., description="A step-by-step investment strategy tailored to the client's profile and objectives.")
    success_metrics: List[str] = Field(..., description="A list of key performance indicators (KPIs) to measure the success of the investment.") 