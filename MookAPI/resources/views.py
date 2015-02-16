import flask
import documents
from documents.exercise_question import *
from MookAPI.hierarchy import documents as hierarchy_documents
from . import bp


@bp.route("/")
def get_resources():
	"""GET list of all resources"""

	print ("GETTING list of all resources")
	
	resources = documents.Resource.objects.order_by('lesson', 'order', 'title').all()
	return flask.jsonify(resources=resources)

@bp.route("/lesson/<lesson_id>")
def get_lesson_resources(lesson_id):
	"""GET list of all resources in given lesson"""

	print ("GETTING list of all resources in lesson {lesson_id}".format(lesson_id=lesson_id))
	
	resources = documents.Resource.objects.order_by('order', 'title').filter(lesson=lesson_id)
	return flask.jsonify(resources=resources)

@bp.route("/skill/<skill_id>")
def get_skill_resources(skill_id):
	"""GET list of all resources in given skill"""

	print ("GETTING list of all resources in skill {skill_id}".format(skill_id=skill_id))
	
	lessons = hierarchy_documents.Lesson.objects.order_by('order', 'title').filter(skill=skill_id)
	resources = documents.Resource.objects.order_by('lesson', 'order', 'title').filter(lesson__in=lessons)
	return flask.jsonify(resources=resources)

@bp.route("/<resource_id>")
def get_resource(resource_id):
	"""GET one resource"""

	print ("GETTING resource with id {resource_id}".format(resource_id=resource_id))
	
	resource = documents.Resource.get_unique_object_or_404(resource_id)
	return flask.jsonify(resource=resource)

@bp.route("/<resource_id>/hierarchy")
def get_resource_hierarchy(resource_id):
	"""GET one resource"""

	print ("GETTING resource with id {resource_id}".format(resource_id=resource_id))
	
	resource = documents.Resource.get_unique_object_or_404(resource_id)
	
	lesson = resource.lesson
	skill = lesson.skill
	track = skill.track
	
	return flask.jsonify(
		resource=resource,
		lesson=lesson,
		skill=skill,
		track=track,
		siblings=resource.siblings(),
		aunts=resource.aunts(),
		cousins=resource.cousins()
	)

@bp.route("/tests/create_exercise")
def test_create_exercise():
	
	question1 = unique_answer_mcq.UniqueAnswerMCQExerciseQuestion()
	q1prop1 = unique_answer_mcq.UniqueAnswerMCQExerciseQuestionProposition()
	q1prop1.text = "A"
	q1prop2 = unique_answer_mcq.UniqueAnswerMCQExerciseQuestionProposition()
	q1prop2.text = "B"
	q1prop3 = unique_answer_mcq.UniqueAnswerMCQExerciseQuestionProposition()
	q1prop3.text = "C"
	q1prop4 = unique_answer_mcq.UniqueAnswerMCQExerciseQuestionProposition()
	q1prop4.text = "D"
	question1.question_text = "La voyelle ?"
	question1.right_proposition = q1prop1
	question1.wrong_propositions = [q1prop2, q1prop3, q1prop4]

	
	question2 = multiple_answer_mcq.MultipleAnswerMCQExerciseQuestion()
	q2prop1 = multiple_answer_mcq.MultipleAnswerMCQExerciseQuestionProposition()
	q2prop1.text = "E"
	q2prop2 = multiple_answer_mcq.MultipleAnswerMCQExerciseQuestionProposition()
	q2prop2.text = "F"
	q2prop3 = multiple_answer_mcq.MultipleAnswerMCQExerciseQuestionProposition()
	q2prop3.text = "G"
	q2prop4 = multiple_answer_mcq.MultipleAnswerMCQExerciseQuestionProposition()
	q2prop4.text = "H"
	question2.question_text = "Les consonnes ?"
	question2.wrong_propositions = [q2prop1]
	question2.right_propositions = [q2prop2, q2prop3, q2prop4]
	
	exercise_content = documents.exercise.ExerciseResourceContent()
	exercise_content.questions = [question1, question2]

	exercise = documents.exercise.ExerciseResource()
	exercise.title = "Alphabet"
	exercise.description = "Pour apprendre les lettres"
	exercise.lesson = hierarchy_documents.Lesson.objects.first()
	exercise.resource_content = exercise_content

	exercise.save()

	return flask.jsonify(exercise=exercise)
