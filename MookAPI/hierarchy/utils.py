from flask import url_for
import hierachy.documents as hierarchyDocuments
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
	track = documents.Track.get_unique_object_or_404(trackId)
	nbValidatedSkill = 0
	skillList = track.skills()
	for skill in skillList:
		skillValidated = getSkillValidated(skill.id)
		if skillValidated: nbValidatedSkill += 1
	return {'current': nbValidatedSkill, 'max': len(skillList)}

def getSkillProgress(skillId):
	skill = documents.Skill.get_unique_object_or_404(skillId)
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
		breadcrumb.push({'title': resourceHierarchyDocument.title, 'url': url_for('hierarchy.get_track', track_id=ob.id, _external=True)})
	elif isinstance(resourceHierarchyDocument, hierarchyDocuments.Skill):
		track = resourceHierarchyDocument.track;
		breadcrumb.push({'title': track.title, 'url': url_for('hierarchy.get_track', track_id=track.id, _external=True)})
		breadcrumb.push({'title': resourceHierarchyDocument.title, 'url': url_for('hierarchy.get_skill', skill_id=resourceHierarchyDocument.id, _external=True)})
	elif isinstance(resourceHierarchyDocument, resourceDocuments.Resource):
		lesson = resourceHierarchyDocument.lesson
		skill = lesson.skill
		track = skill.track
		breadcrumb.push({'title': track.title, 'url': url_for('hierarchy.get_track', track_id=track.id, _external=True)})
		breadcrumb.push({'title': skill.title, 'url': url_for('hierarchy.get_skill', skill_id=skill.id, _external=True)})
		breadcrumb.push({'title': resourceHierarchyDocument.title, 'url': url_for('resources.get_resource', resource_id=resourceHierarchyDocument.id, _external=True)})
	return breadcrumb
