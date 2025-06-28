from pydantic import BaseModel, Field
from typing import List, Optional

class RealEstateTrend(BaseModel):
    """Represents a single real estate trend."""
    trend_name: str = Field(..., description="The name of the trend, e.g., 'Price Appreciation', 'Market Growth'.")
    trend_description: str = Field(..., description="A detailed description of the trend.")
    supporting_data_points: List[str] = Field(default_factory=list, description="A list of data points or facts supporting the trend.")

class MarketData(BaseModel):
    """Represents key market data points."""
    metric_name: str = Field(..., description="The name of the metric, e.g., 'Median Home Price', 'Average Rent'.")
    value: str = Field(..., description="The value of the metric.")
    region: Optional[str] = Field(None, description="The geographical region for the data, if applicable.")
    source: Optional[str] = Field(None, description="The source of the data.")
    property_type: Optional[str] = Field(None, description="The type of property, e.g., 'apartment', 'house'.")
    number_of_bedrooms: Optional[int] = Field(None, description="The number of bedrooms.")
    number_of_bathrooms: Optional[int] = Field(None, description="The number of bathrooms.")
    size_sqft: Optional[float] = Field(None, description="The size of the property in square feet.")
    amenities: Optional[List[str]] = Field(default_factory=list, description="A list of amenities.")

class PropertyDetails(BaseModel):
    """Represents the specific details of a property listing."""
    location: Optional[str] = Field(None, description="The location of the property.")
    price: Optional[str] = Field(None, description="The price of the property.")
    property_type: Optional[str] = Field(None, description="The type of property.")
    size_sqft: Optional[float] = Field(None, description="The size of the property in square feet.")
    number_of_bedrooms: Optional[int] = Field(None, description="The number of bedrooms.")
    number_of_bathrooms: Optional[int] = Field(None, description="The number of bathrooms.")
    amenities: List[str] = Field(default_factory=list, description="A list of amenities.")
    year_built: Optional[int] = Field(None, description="The year the property was built.")
    property_condition: Optional[str] = Field(None, description="The condition of the property.")

class RealEstateAnalysis(BaseModel):
    """The root model for the structured real estate analysis."""
    trends: List[RealEstateTrend] = Field(default_factory=list, description="A list of identified real estate trends.")
    key_market_data: List[MarketData] = Field(default_factory=list, description="A list of key market data points.")
    property_listings: List[PropertyDetails] = Field(default_factory=list, description="A list of specific property listings found.")
    market_outlook: str = Field(..., description="The overall market outlook, e.g., 'Positive', 'Negative', 'Neutral'.")
    raw_text_summary: str = Field(..., description="A summary of the raw text that was analyzed to generate this structured data.") 