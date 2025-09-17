import logging
from app.config import settings
import openai
from typing import Dict,List
import json

logger= logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self.provider = settings.DEFAULT_LLM_PROVIDER
        self.openai_api_key = settings.OPENAI_API_KEY

        # initialize openai client
        if self.openai_api_key:
            openai.api_key = self.openai_api_key

#  Generate a call summary from the transcript and context.
# - Builds a prompt for the LLM.
# - Uses the selected provider (currently OpenAI).
# - Falls back to a basic summary if an error occurs.
# Returns the summary text as a string.

    async def generate_call_summary(
    self,
    transcript: str,
    caller_info: Dict = None,
    call_duration: int = 0,
    call_reason: str = None
)->str:
        """Generate a comprehensive summary from transcript"""

        # create context-aware prompt
        prompt = self.create_summary_prompt(
            transcript, caller_info, call_duration, call_reason
        )

        try:
            if self.provider == "openai":
                return await self._generate_with_openai(prompt)
            else:
                raise ValueError(f"Unsupported LLM provider: {self.provider}")


        except Exception as e:
            logger.error(f"Error generating call summary: {str(e)}")
            return self._create_fallback_summary(transcript, caller_info)

# Create a structured prompt for the LLM to summarize a call,
# including optional caller info, call duration, and the transcript,
# and specify the output format for a warm transfer summary.

    def create_summary_prompt(
        self,
        transcript: str,
        caller_info: Dict = None,
        call_duration: int = 0,
        call_reason: str = None
)-> str:
        """Create a structured prompt for call summarization"""

        caller_context = ""
        if caller_info:
            caller_context = f"""
            Caller Information:
            - Name: {caller_info.get('name','Unknown')}
            - Phone: {caller_info.get('phone','Not provided')}
            - Reason for call: {call_reason or 'Not specified'}
        """
        duration_context = f"Call duration: {call_duration // 60} minutes {call_duration % 60} seconds" if call_duration > 0 else ""

        prompt = f"""
        You are an expert call center analyst. Please analyze the following customer 
        service call transcript and provide a comprehensive summary that would be useful 
        for a warm transfer to another agent.

        {caller_context}
        {duration_context}

        CALL TRANSCRIPT:
        {transcript}

        Please provide a strucutred summary in the following format:

        **CALL SUMMARY**
        - Customer Name: [Extract or use provided]
        - Issue Category: [Categorize the main issue]
        - Key Points: [3-5 bullet points of main discussion points]
        - Customer Sentiment: [Professional assessment]
        - Actions Taken: [What has been done so far]
        - Outstanding Items: [What still needs to be resolved]
        - Recommended Next Steps: [Suggestions for the receiving agent]
        - Priority Level: [Low/Medium/High based on urgency]

        Keep the summary concise but comprehensive, focusing on information that 
        would help the next agent continue the conversation seamlessly.
    """ 
        return prompt    

# Asynchronously send the prompt to OpenAI Chat API to generate a call summary,
# then return the cleaned summary text; logs and raises errors if the API fails.

    async def _generate_with_openai(self, prompt:str)->str:
        """Generate summary using OpenAi API"""

        try:
            response = await openai.ChatCompletion.acreate(
                model = "gpt-3.5-turbo",
                messages = [
                    {"role":"system", "content":"You are a professional call center analyst specializing in creating clear, actionable call summaries for agent handoffs."},
                    {"role":"user","content":prompt}
                ],
                max_tokens = settings.MAX_SUMMARY_TOKENS,
                temperature = settings.SUMMARY_TEMPERATURE,
                timeout = 30
            )
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise

# Generate a simple fallback summary if the LLM is unavailable,
# showing caller name, default placeholders, and a preview of the transcript.

    def _create_fallback_summary(self, transcript:str , caller_info: Dict = None)->str:
        """Create a basic summary when LLM is unavailable"""

        caller_name = caller_info.get('name','Unknown') if caller_info else 'Unknown'
        transcript_preview = transcript[:300]+ "..." if len(transcript) > 300 else transcript

        return f"""
            **CALL SUMMARY** (Auto-generated fallback)
            - Customer Name: {caller_name}
            - Issue Category: Requires agent review
            - Key Points: Please review full transcript for details
            - Customer Sentiment: Requires assessment
            - Actions Taken: To be determined by reviewing agent
            - Outstanding Items: All items require attention
            - Recommended Next Steps: Review complete call transcript and continue assistance
            - Priority Level: Medium

            **Transcript Preview:**
            {transcript_preview}

            Note: This is a fallback summary. Please review the complete transcript for full context.
    """

# Generate a brief, professional transfer message for agent handoff,
# using OpenAI when available, otherwise falling back to a default template.

    async def generate_transfer_context(
        self,
        summary: str,
        transfer_reason: str,
        agent_skills: List[str] = None
)->str:
        """Generate context for agent-to-agent transfer"""

        skills_context = f"Receiving agent skills: {', '.join(agent_skills)}" if agent_skills else ""
        prompt = f"""
        You are helping with a warm call transfer. Please create a brief,
        professional transfer message that Agent A should communicate to Agent B.

        Call Summary:
        {summary}

        Transfer Reason: {transfer_reason}
        {skills_context}

        Create a concise transfer message (2-3 sentences) that Agent A can speak to Agent B, covering:
        1. Brief customer situation
        2. What's been done
        3. What needs to happen next

        Make it conversational and professional, as if one agent is speaking directly to another.
    """
        try:
            if self.provider == "openai":
                response = await openai.ChatCompletion.acreate(
                    model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are helping create professional agent-to-agent transfer communications."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=150,
                        temperature=0.3,
                        timeout=15
                )
                return response.choices[0].message.content.strip()
            
            else:
                # Fallback for other providers or if OpenAI fails
                return f"Hi, I'm transferring a call to you. {transfer_reason}. The customer has been helped with their initial inquiry, and now needs your expertise to continue. Please see the full summary for details."
        
        except Exception as e:
            logger.error(f"Error generating transfer context: {str(e)}")
            return f"Hi, I'm transferring a call to you. {transfer_reason}. Please check the call summary for full context."        

# Analyze call transcript sentiment using OpenAI and return a structured JSON.
# Falls back to a neutral default response if analysis fails.

    async def analyze_call_sentiment(self, transcript:str)->Dict:
        """Analyze customer sentiment from transcript"""

        prompt = f"""
        Analyze the customer sentiment in this call transcript and provide a JSON response:

        Transcript: {transcript[:1000]}...

        Provide analysis in this exact JSON format:
        {{
            "overall_sentiment": "positive|neutral|negative",
            "confidence": 0.85,
            "key_emotions": ["satisfied", "frustrated", "confused"],
            "escalation_risk": "low|medium|high",
            "summary": "Brief sentiment summary"
        }}  
    """
        try:
            if self.provider == "openai":
                response = await openai.ChatCompletion.acreate(
                    model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are an expert in customer sentiment analysis. Always respond with valid JSON."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=200,
                        temperature=0.1,
                        timeout=20
                )
                content = response.choices[0].message.content.strip()
                return json.loads(content)
        
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {str(e)}")

        # fallback response
        return {
            "overall_sentiment": "neutral",
            "confidence": 0.5,
            "key_emotions": ["unknown"],
            "escalation_risk": "medium",
            "summary": "Sentiment analysis unavailable"
        }    

# Create singleton instance
llm_service = LLMService()