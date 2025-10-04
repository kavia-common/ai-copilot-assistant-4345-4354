from pydantic import BaseModel, Field

# PUBLIC_INTERFACE
class AskRequest(BaseModel):
    """Schema for questions sent from the frontend to the backend."""
    question: str = Field(..., description="The user's question to be answered by the AI.")

# PUBLIC_INTERFACE
class AskResponse(BaseModel):
    """Schema for answers returned by the backend after calling the AI model."""
    answer: str = Field(..., description="The AI-generated answer for the given question.")
    model: str | None = Field(None, description="The model used to generate the answer, if available.")
