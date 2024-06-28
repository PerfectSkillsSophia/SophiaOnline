from django.shortcuts import render , redirect
from Accounts.views import logoutUser
from Administration. models import *
from Assessments.models import *
from django.http import JsonResponse
import random
import string
from django.contrib.auth.decorators import login_required


def generate_random_code():
    characters = string.ascii_letters + string.digits
    code = ''.join(random.choice(characters) for i in range(7))
    return code



@login_required(login_url='login')
def Assessments_Dashboard (request):
			return render(request,'assessments_dashboard.html')

@login_required(login_url='login')
def Start_Assessments (request):
		if request.method == 'GET':
			assessment_code = request.GET.get('assessment_code')
			if assessment_code:
				username = request.user
				assessment=Assessment.objects.get(assessment_code=assessment_code)
				assessment_name = assessment.assessment_name
				return render(request, 'start_assessments.html', {'assessment_code': assessment_code,'username':username,'assessment_name':assessment_name})		
			else:
				return render(request,'assessments_dashboard.html')
			
@login_required(login_url='login')
def Assessments (request,assessment_code):
		assessment=Assessment.objects.get(assessment_code=assessment_code)
		allque = Assessment.objects.get(assessment_code=assessment_code).question_set.all()
		username = request.user
		assessment_name = assessment.assessment_name
		return render(request,'assessment.html',{'question': allque,'username':username,'assessment_name':assessment_name})

@login_required(login_url='login')
def feedback_page(request):
	return render(request,'feedback.html')

@login_required(login_url='login')
def feedback(request):
    if request.method == 'POST':
        # Create a Feedback object with user and feedback type and save to database
        feedback_type = request.POST.get('feedback_type')
        feedback = Feedback(user_name=request.user, feedback_type=feedback_type)
        feedback.save()
        # Redirect to thank you page
        return redirect(logoutUser)
	

@login_required(login_url='login')
def Upload_Video(request):
    if request.method == 'POST':
        print("POST request received.")
        uploaded_files = request.FILES.values()
        assessment_name = request.POST.get('ass_name').strip()  # Strip whitespace
        print(f"Assessment name (stripped): '{assessment_name}'")  # Print stripped assessment name
        
        try:
            assessment = Assessment.objects.get(assessment_name__iexact=assessment_name)
            assessment_type = assessment.assessment_type
            print(f"Assessment type: {assessment_type}")
        except Assessment.DoesNotExist:
            print(f"Assessment '{assessment_name}' not found.")
            return JsonResponse({'error': 'Assessment not found'}, status=404)

        question_ids = []
        question_ids_get = request.POST.get('question_ids')
        print(f"Question IDs: {question_ids_get}")
        for i in question_ids_get.split(','):
            question_ids.append(i)
        
        submission_id = generate_random_code()
        print(f"Generated submission ID: {submission_id}")
        
        for index, uploaded_file in enumerate(uploaded_files):
            id = question_ids[index]
            print(f"Processing question ID: {id}")
            try:
                question = Question.objects.get(questionId=id)
                q = question.question
                ca = question.correctanswer
                print(f"Question: {q}, Correct answer: {ca}")
            except Question.DoesNotExist:
                print(f"Question with ID {id} not found.")
                return JsonResponse({'error': f'Question with ID {id} not found'}, status=404)

            Recording.objects.create(
                video=uploaded_file,
                user_name=request.user,
                assessment_name=assessment_name,
                submission_id=submission_id,
                question_id=id,
                que=q,
                c_ans=ca,
                assessmenttype=assessment_type
            )
            print(f"Recording created for question ID: {id}")

        FinalResult.objects.create(
            submission_id=submission_id,
            user_name=request.user,
            assessment_name=assessment_name,
            assessment_type=assessment_type
        )
        print("Final result created.")
        return JsonResponse({'success': True})

    else:
        print("Invalid request method.")
        return JsonResponse({'error': 'Invalid request method'}, status=405)