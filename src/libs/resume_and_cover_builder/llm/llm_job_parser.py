import os
import tempfile
import textwrap
import time
import re  # For email validation
from src.libs.resume_and_cover_builder.utils import LoggerChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
from loguru import logger
from pathlib import Path
from langchain_core.prompt_values import StringPromptValue
from langchain_core.runnables import RunnablePassthrough
from langchain_text_splitters import TokenTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from src.libs.resume_and_cover_builder.config import global_config
from langchain_community.document_loaders import TextLoader
from requests.exceptions import HTTPError as HTTPStatusError  # HTTP error handling
import openai

# Load environment variables from the .env file
load_dotenv()

# Configure the log file
log_folder = 'log/resume/gpt_resume'
if not os.path.exists(log_folder):
    os.makedirs(log_folder)
log_path = Path(log_folder).resolve()
logger.add(log_path / "gpt_resume.log", rotation="1 day", compression="zip", retention="7 days", level="DEBUG")


class LLMParser:
    def __init__(self, openai_api_key):
        self.llm = LoggerChatModel(
            ChatOpenAI(
                model_name="gpt-4o-mini", openai_api_key=openai_api_key, temperature=0.4
            )
        )
        self.llm_embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)  # Initialize embeddings
        self.vectorstore = None  # Will be initialized after document loading

    @staticmethod
    def _preprocess_template_string(template: str) -> str:
        """
        Preprocess the template string by removing leading whitespaces and indentation.
        Args:
            template (str): The template string to preprocess.
        Returns:
            str: The preprocessed template string.
        """
        return textwrap.dedent(template)
    
    def set_body_html(self, body_html):
        """
        Retrieves the job description from HTML, processes it, and initializes the vectorstore.
        Args:
            body_html (str): The HTML content to process.
        """

        # Save the HTML content to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode="w", encoding="utf-8") as temp_file:
            temp_file.write(body_html)
            temp_file_path = temp_file.name 
        try:
            loader = TextLoader(temp_file_path, encoding="utf-8", autodetect_encoding=True)
            document = loader.load()
            logger.debug("Document successfully loaded.")
        except Exception as e:
            logger.error(f"Error during document loading: {e}")
            raise
        finally:
            os.remove(temp_file_path)
            logger.debug(f"Temporary file removed: {temp_file_path}")
        
        # Split the text into chunks
        text_splitter = TokenTextSplitter(chunk_size=500, chunk_overlap=50)
        all_splits = text_splitter.split_documents(document)
        logger.debug(f"Text split into {len(all_splits)} fragments.")
        
        # Create the vectorstore using FAISS
        try:
            self.vectorstore = FAISS.from_documents(documents=all_splits, embedding=self.llm_embeddings)
            logger.debug("Vectorstore successfully initialized.")
        except Exception as e:
            logger.error(f"Error during vectorstore creation: {e}")
            raise

    def _retrieve_context(self, query: str, top_k: int = 3) -> str:
        """
        Retrieves the most relevant text fragments using the retriever.
        Args:
            query (str): The search query.
            top_k (int): Number of fragments to retrieve.
        Returns:
            str: Concatenated text fragments.
        """
        if not self.vectorstore:
            raise ValueError("Vectorstore not initialized. Run extract_job_description first.")
        
        retriever = self.vectorstore.as_retriever()
        retrieved_docs = retriever.get_relevant_documents(query)[:top_k]
        context = "\n\n".join(doc.page_content for doc in retrieved_docs)
        logger.debug(f"Context retrieved for query '{query}': {context[:200]}...")  # Log the first 200 characters
        return context
    
    def _extract_information(self, question: str, retrieval_query: str) -> str:
        """
        Generic method to extract specific information using the retriever and LLM.
        Args:
            question (str): The question to ask the LLM for extraction.
            retrieval_query (str): The query to use for retrieving relevant context.
        Returns:
            str: The extracted information.
        """
        context = self._retrieve_context(retrieval_query)
        
        prompt = ChatPromptTemplate.from_template(
            template="""
            You are an expert in extracting specific information from job descriptions. 
            Carefully read the job description context below and provide a clear and concise answer to the question.

            Context: {context}

            Question: {question}
            Answer:
            """
        )
        
        formatted_prompt = prompt.format(context=context, question=question)
        logger.debug(f"Formatted prompt for extraction: {formatted_prompt[:200]}...")  # Log the first 200 characters
        
        try:
            chain = prompt | self.llm | StrOutputParser()
            result = chain.invoke({"context": context, "question": question})
            extracted_info = result.strip()
            logger.debug(f"Extracted information: {extracted_info}")
            return extracted_info
        except Exception as e:  
            logger.error(f"Error during information extraction: {e}")
            return ""
    
    def extract_job_description(self) -> str:
        """
        Extracts the company name from the job description.
        Returns:
            str: The extracted job description.
        """
        question = "What is the job description of the company?"
        retrieval_query = "Job description"
        logger.debug("Starting job description extraction.")
        return self._extract_information(question, retrieval_query)
    
    def extract_company_name(self) -> str:
        """
        Extracts the company name from the job description.
        Returns:
            str: The extracted company name.
        """
        question = "What is the company's name?"
        retrieval_query = "Company name"
        logger.debug("Starting company name extraction.")
        return self._extract_information(question, retrieval_query)
    
    def extract_role(self) -> str:
        """
        Extracts the sought role/title from the job description.
        Returns:
            str: The extracted role/title.
        """
        question = "What is the role or title sought in this job description?"
        retrieval_query = "Job title"
        logger.debug("Starting role/title extraction.")
        return self._extract_information(question, retrieval_query)
    
    def extract_location(self) -> str:
        """
        Extracts the location from the job description.
        Returns:
            str: The extracted location.
        """
        question = "What is the location mentioned in this job description?"
        retrieval_query = "Location"
        logger.debug("Starting location extraction.")
        return self._extract_information(question, retrieval_query)
    
    def extract_recruiter_email(self) -> str:
        """
        Extracts the recruiter's email from the job description.
        Returns:
            str: The extracted recruiter's email.
        """
        question = "What is the recruiter's email address in this job description?"
        retrieval_query = "Recruiter email"
        logger.debug("Starting recruiter email extraction.")
        email = self._extract_information(question, retrieval_query)
        
        # Validate the extracted email using regex
        email_regex = r'[\w\.-]+@[\w\.-]+\.\w+'
        if re.match(email_regex, email):
            logger.debug("Valid recruiter's email.")
            return email
        else:
            logger.warning("Invalid or not found recruiter's email.")
            return ""
 
