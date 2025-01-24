from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.llms import Ollama
import os
from dotenv import load_dotenv
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import ChatMessage
from authapp.models import Demographics
from datetime import datetime

def chatbot_view(request):
    return render(request, 'chatbot.html')  

load_dotenv()

langchain_api_key = os.getenv("LANGCHAIN_API_KEY")
if langchain_api_key is None:
    raise ValueError("LANGCHAIN_API_KEY is not set in the environment or .env file")

os.environ["LANGCHAIN_API_KEY"] = langchain_api_key
os.environ["LANGCHAIN_TRACING_V2"] = "true"


llm = Ollama(model="llama3.2:1b")

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a fitness trainer. User demographics (Age, Gender, Height, Weight, Fitness Goal, Activity Level) are provided with each query. Use this information to provide personalized fitness advice and respond to the user's queries."),
    ("user", "Question: {question}")
])

output_parser = StrOutputParser()
chain = prompt | llm | output_parser

@csrf_exempt
@login_required
def clear_chat(request):
    """Clear the chat history from the database"""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            # Clear chat history from database
            ChatMessage.clear_chat_history(request.user, request.session.session_key)
            # Also clear session chat history
            request.session['chat_history'] = []
            request.session.modified = True
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

@csrf_exempt
@login_required
def chatbot_view(request):
    # Ensure we have a session key
    if not request.session.session_key:
        request.session.create()
    
    # Get chat history from database and convert to list of dicts
    chat_history = [
        {
            'role': msg.role,
            'content': msg.content,
            'timestamp': msg.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }
        for msg in ChatMessage.get_chat_history(request.user, request.session.session_key)
    ]

    print(f"[DEBUG] Session Key: {request.session.session_key}")
    print(f"[DEBUG] Chat History from DB count: {len(chat_history)}")
    
    # Get user demographics
    demographics_data = None
    try:
        demographics_data = request.user.demographics
        # Format demographics into a string or dictionary for the prompt
        demographics_string = f"User Demographics: Age - {demographics_data.age}, Gender - {demographics_data.gender}, Height - {demographics_data.height}cm, Weight - {demographics_data.weight}kg, Fitness Goal - {demographics_data.get_fitness_goal_display()}, Activity Level - {demographics_data.get_activity_level_display()}."
    except Demographics.DoesNotExist:
        demographics_string = "User demographics not available."

    if request.method == 'POST':
        user_input = request.POST.get('user_input')
        # Retrieve demographics data sent from frontend (optional, as we fetch it here)
        # frontend_demographics = request.POST.get('demographics') # Example if sent from frontend

        if not user_input:
            return JsonResponse({'error': 'No message provided'}, status=400)
        
        try:
            # Combine user input with demographics for the prompt
            full_prompt = f"{demographics_string}\nUser Query: {user_input}"
            print(f"[DEBUG] Full prompt sent to chain: {full_prompt}")

            # Generate response
            response = chain.invoke({"question": full_prompt})
            
            # Save messages to database
            user_message = ChatMessage.objects.create(
                user=request.user,
                role='user',
                content=user_input, # Save original user input
                session_id=request.session.session_key
            )
            bot_message = ChatMessage.objects.create(
                user=request.user,
                role='assistant',
                content=response,
                session_id=request.session.session_key
            )
            
            # Add new messages to chat history (using original user input)
            chat_history.extend([
                {
                    'role': 'user',
                    'content': user_input,
                    'timestamp': user_message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
                },
                {
                    'role': 'assistant',
                    'content': response,
                    'timestamp': bot_message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
                }
            ])
            
            # Return JSON response for AJAX requests
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # Refetch chat history to ensure all messages are included
                updated_chat_history = [
                    {
                        'role': msg.role,
                        'content': msg.content,
                        'timestamp': msg.timestamp.strftime('%Y-%m-%d %H%M%S') # Use consistent format
                    }
                    for msg in ChatMessage.get_chat_history(request.user, request.session.session_key)
                ]
                return JsonResponse({
                    'role': 'assistant',
                    'content': response,
                    'chat_history': updated_chat_history
                })
            
        except Exception as e:
            print(f"Error in chatbot view: {str(e)}")  # Log the error
            # Hide typing indicator on error (handled in frontend JS finally block)
            error_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S') # Use consistent format
            # Append error message to history for display
            chat_history.append({
                 'role': 'assistant',
                 'content': 'Sorry, there was an error processing your message. Please try again.',
                 'timestamp': error_timestamp
            })
            return JsonResponse({
                'error': 'Failed to process message',
                'details': str(e),
                'chat_history': chat_history # Return updated history with error
            }, status=500)
    
    # For GET requests, render the full template with chat history and demographics
    return render(request, 'chatbot.html', {
        'chat_history': chat_history,
        'session_id': request.session.session_key,  # Pass session ID to template for debugging
        'demographics': demographics_data # Pass demographics to template
    })
