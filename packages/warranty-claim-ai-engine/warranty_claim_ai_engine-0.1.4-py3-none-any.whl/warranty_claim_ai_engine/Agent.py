from typing import Dict, List, Any, Optional, TypedDict, Annotated
import os
import json
import operator
from langgraph.graph import StateGraph, END
from langchain.schema import HumanMessage, SystemMessage, AIMessage, BaseMessage
from model import create_model
from ocr import OCRProcessor
from rag_system import PolicyRAGSystem

class ProcessingState(TypedDict):
    """State for claim processing workflow."""
    messages: Optional[List[BaseMessage]]
    form_data: Any
    image_data: Optional[str]
    image_files: Any
    historical_claims: Any
    extracted_data: Any
    enhanced_data: Any
    validation_result: Any
    fraud_analysis: Any
    policy_analysis: Any
    final_decision: Any

class WarrantyClaimAgent:
    def __init__(self, model_provider: str = None, model_name: str = None,api_key = None, policy_dir: str = None, vector_db_dir: str = None):
        self.model = create_model(model_provider, model_name,api_key)
        self.ocr_processor = OCRProcessor()
        self.rag_system = PolicyRAGSystem(policy_dir, vector_db_dir)
        self.graph = self.build_processing_graph()
    
    def build_processing_graph(self):
        workflow = StateGraph(ProcessingState)
        workflow.add_node("intake_node", self.claim_intake_node)
        workflow.add_node("validation_node", self.validation_node)
        workflow.add_node("fraud_detection_node", self.fraud_detection_node)
        workflow.add_node("policy_check_node", self.policy_check_node)
        workflow.add_node("adjudication_node", self.adjudication_node)
        workflow.set_entry_point("intake_node")
        workflow.add_edge("intake_node", "validation_node")
        workflow.add_edge("validation_node", "fraud_detection_node")
        workflow.add_edge("fraud_detection_node", "policy_check_node")
        workflow.add_edge("policy_check_node", "adjudication_node")
        workflow.add_edge("adjudication_node", END)
        return workflow.compile()
    
    def claim_intake_node(self, state: ProcessingState):
        """Process claim intake using LLM Intelligence"""
        try:
            if state["form_data"]:
                form_analysis = self.analyze_form_data(state["form_data"])
                state['extracted_data'] = form_analysis
            
            if state["image_files"]:
                image_analysis = self.analyze_images(state["image_files"])
                state["image_data"] = image_analysis
            
            data = f"""{state["extracted_data"]} and {state["image_data"]} enhance this data and 
            provide a structured data"""
            
            # FIX 1: Pass messages as list to invoke
            messages = [HumanMessage(content=data)]
            enhanced_data = self.model.invoke(messages)
            
            # FIX 2: Properly append messages - enhanced_data is already an AIMessage
            state["messages"].append(HumanMessage(content=data))
            state["messages"].append(enhanced_data)
            
            # Extract content from AIMessage
            state["enhanced_data"] = enhanced_data.content if hasattr(enhanced_data, 'content') else str(enhanced_data)
            
            print("Claim Intake Node Executed Successfully")
            return state
        except Exception as e:
            print(f"Error in claim intake: {str(e)}")
            return state
    
    def validation_node(self, state: ProcessingState):
        """Validate claim using LLM reasoning"""
        try:
            data = state["enhanced_data"]
            validation_prompt = f"""you are a warranty claim validation expert. analyze the following claim data {data} and determine its validity from your 
            knowledge base please assess:
            1. data completeness and quality
            2. warranty period validity
            3. claim legitimacy indicators
            4. missing information that might be needed
            provide your analysis in detailed way and it must include
            is_valid,issues found , missing_data,recommendations,reasoning
            in response format in a structured way not json or dict just String format like how real humans do like readable Document"""
            
            messages = state.get("messages", [])
            messages.append(HumanMessage(content=validation_prompt))
            
            # FIX 3: Pass messages to invoke
            validation_response = self.model.invoke(messages)
            
            # validation_response is already an AIMessage
            state["messages"].append(validation_response)
            state["validation_result"] = validation_response.content if hasattr(validation_response, 'content') else str(validation_response)
            
            print("Validation Node Executed Successfully")
            return state
        except Exception as e:
            print(f"Error in validation: {str(e)}")
            return state
    
    def fraud_detection_node(self, state: ProcessingState):
        """Detect fraud using LLM analysis"""
        try:
            data = state["enhanced_data"]
            validation_data = state["validation_result"]
            historical_claims = state["historical_claims"]
            
            fraud_prompt = f"""You are a fraud detection expert specializing in warranty claims. Analyze the following claim for potential fraud indicators.

            Current Claim:
            {data}

            Historical Claims (for pattern analysis):
            {historical_claims} 
            validated_data:{validation_data}
            Analyze for:
            1. Suspicious timing patterns
            2. Unusual claim amounts vs product value
            3. Vague or inconsistent descriptions
            4. Potential duplicate claims
            5. Customer behavioral patterns
            6. Technical feasibility of claimed issues
            and so on if i miss any major analysis in these make sure to add it 
            provide the output in a structured way and these are must
            fraud_detected,fraud_score,risk_level,fruad_indicators,
            suspicious_patterns,confidence,reasoning,recommendations and response format in a structured way not json or dict just String format like how real humans do like readable Document"""
            
            messages = state.get("messages", [])
            messages.append(HumanMessage(content=fraud_prompt))
            fraud_response = self.model.invoke(fraud_prompt)
            
            state["messages"].append(fraud_response)
            state["fraud_analysis"] = fraud_response.content if hasattr(fraud_response, 'content') else str(fraud_response)
            
            print("Fraud Detection Node Executed Successfully")
            return state
        except Exception as e:
            print(f"Error in fraud detection: {str(e)}")
            return state
    
    def policy_check_node(self, state: ProcessingState) -> ProcessingState:
        """Check claim against warranty policies using extracted RAG data and LLM."""
        try:
            data = state["enhanced_data"]
            rag_result = self.rag_system.search_relevant_policies(data, top_k=8)
            
            policy_prompt = f"""
                you are a warranty policy expert analyze the following claim against the 
                warranty policy information claim details:
                {data} relevent policy information:
                {rag_result}  Determine:
            1. Is this claim covered under the warranty policy?
            2. What specific policy sections apply?
            3. Are there any exclusions that might apply?
            4. What is the confidence level of this assessment?
            you must provide is_covered, coverage_confidence,applicable_sections,
            exclusions_apply,coverage_percentage,reasoning(detailed explaination),policy_excerpts and response format in a structured way not json or dict just String format like how real humans do like readable Document"""
            
            messages = state.get("messages", [])
            messages.append(HumanMessage(content=policy_prompt))
            
            # FIX 5: Pass messages to invoke
            policy_response = self.model.invoke(policy_prompt)
            
            state["messages"].append(policy_response)
            state["policy_analysis"] = policy_response.content if hasattr(policy_response, 'content') else str(policy_response)
            
            print("Policy Check Node Executed Successfully")
            return state
        except Exception as e:
            print(f"Error in policy check: {str(e)}")
            return state
    
    def adjudication_node(self, state: ProcessingState) -> ProcessingState:
        """Make final claim decision using LLM reasoning."""
        try:
            data = state["enhanced_data"]
            validation_data = state["validation_result"]
            fraud_data = state["fraud_analysis"]
            policy_data = state["policy_analysis"]
            
            adjudication_prompt = f"""
            You are a senior warranty claim adjudicator making the final decision on this claim.
            Claim Data:{data}
            Validation Analysis:{validation_data}
            Fraud Analysis:{fraud_data}
            Policy Analysis:{policy_data}
            based on all this information make your final decision consider
            1. Is the claim valid and covered by warranty?
            2. What is the fraud risk level?
            3. Should this be approved, denied, or require manual review?
            4. If approved, what amount should be covered?
            "You are a fair and thorough claim adjudicator. Make decisions based on evidence and policy. Explain your reasoning clearly."
            and give a detailed analysis report and that must include
            decision,approved_amount,confidence,decision_factors,reasoning,next_actions,customer_message,review_required
            in a structured way.if "Claim requires manual review due to high fraud risk or policy ambiguity",
             define "next_actions"["Manual review by senior adjudicator", "Request additional documentation"] and as i told you give a comprehensive detailed report on this warranty claim like how real humans do like readable Document from the beggining user data details to
            end """
            
            messages = state.get("messages", [])
            messages.append(HumanMessage(content=adjudication_prompt))
            
            adjudication_response = self.model.invoke(adjudication_prompt)
            
            state["messages"].append(adjudication_response)
            state["final_decision"] = adjudication_response.content if hasattr(adjudication_response, 'content') else str(adjudication_response)
            
            print("Adjudication Node Executed Successfully")
            return state
        except Exception as e:
            print(f"Error in adjudication: {str(e)}")
            return state
    
    def analyze_form_data(self, form_data):
        """Use LLM to analyze and structure form data."""
        prompt = f"""
        Analyze the following warranty claim form data and extract structured information:Form Data:{form_data}"""
        
        messages = [HumanMessage(content=prompt)]
        response = self.model.invoke(messages)
        
        return response.content if hasattr(response, 'content') else str(response)
    
    def analyze_images(self, image_files):
        """Use EasyOCR + LLM to analyze uploaded images."""
        ocr_result = self.ocr_processor.extract_text_from_image(image_files)
        
        prompt = f"""
        Analyze the following text extracted from warranty claim documents:Extracted Text:{ocr_result}
        Extract structured information:
        - customer_info: any customer details found
        - product_info: product details, serial numbers, purchase info
        - claim_details: issue descriptions, amounts, dates
        - document_types: types of documents detected
        """
        
        messages = [HumanMessage(content=prompt)]
        response = self.model.invoke(messages)
        
        return response.content if hasattr(response, 'content') else str(response)
    
    def process_claim(self, form_data, image_files, historical_claims):
        """process a warranty claim"""
        initial_state = ProcessingState(
            messages=[],
            form_data=form_data,
            image_data=None,
            image_files=image_files,
            historical_claims=historical_claims,
            extracted_data=None,
            enhanced_data=None,
            validation_result=None,
            fraud_analysis=None,
            policy_analysis=None,
            final_decision=None
        )
        
        try:
            result = self.graph.invoke(initial_state)
            return result, f"""final_decision":{result["final_decision"]}"""
        
        except Exception as e:
            return f"Failed to process claim: {str(e)}", None