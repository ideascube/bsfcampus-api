from flask import url_for
import hierarchy.documents as hierarchyDocuments
import resources.documents as resourceDocuments
from random import randint

# #FIXME: the calculation of the progress is done randomly until we have a real user account management, which keeps track of actual user's progress
def getTrackValidated(trackId):
	rd = randint(0, 99)
	return (rd < 50)

# #FIXME: the calculation of the progress is done randomly until we have a real user account management, which keeps track of actual user's progress
def getSkillValidated(skillId):
	rd = randint(0, 99)
	return (rd < 50)

# #FIXME: the calculation of the progress is done randomly until we have a real user account management, which keeps track of actual user's progress
def getResourceValidated(resourceId):
	rd = randint(0, 99)
	return (rd < 50)

def getTrackProgress(trackId):
	track = hierarchyDocuments.Track.get_unique_object_or_404(trackId)
	nbValidatedSkill = 0
	skillList = track.skills()
	for skill in skillList:
		skillValidated = getSkillValidated(skill.id)
		if skillValidated: nbValidatedSkill += 1
	return {'current': nbValidatedSkill, 'max': len(skillList)}

def getSkillProgress(skillId):
	skill = hierarchyDocuments.Skill.get_unique_object_or_404(skillId)
	nbChildrenResources = 0
	nbValidatedResources = 0
	for lesson in skill.lessons():
		nbChildrenResources += len(lesson.resources())
		for resource in lesson.resources():
			resourceValidated = getResourceValidated(resource.id)
			if resourceValidated: nbValidatedResources += 1
	return {'current': nbValidatedResources, 'max': nbChildrenResources}

def generateBreadcrumb(resourceHierarchyDocument):
	breadcrumb = []
	if isinstance(resourceHierarchyDocument, hierarchyDocuments.Track):
		breadcrumb.append({'title': resourceHierarchyDocument.title, 'track_id': resourceHierarchyDocument.id})
	elif isinstance(resourceHierarchyDocument, hierarchyDocuments.Skill):
		track = resourceHierarchyDocument.track;
		breadcrumb.append({'title': track.title, 'track_id': track.id})
		breadcrumb.append({'title': resourceHierarchyDocument.title, 'skill_id': resourceHierarchyDocument.id})
	elif isinstance(resourceHierarchyDocument, resourceDocuments.Resource):
		lesson = resourceHierarchyDocument.lesson
		skill = lesson.skill
		track = skill.track
		breadcrumb.append({'title': track.title, 'track_id': track.id})
		breadcrumb.append({'title': skill.title, 'skill_id': skill.id})
		breadcrumb.append({'title': resourceHierarchyDocument.title, 'resource_id': resourceHierarchyDocument.id})
	return breadcrumb
