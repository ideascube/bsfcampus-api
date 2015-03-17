import documents
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

# #FIXME: the calculation of the progress is done randomly until we have a real user account management, which keeps track of actual user's progress
def getTrackProgress(trackId):
	track = documents.Track.get_unique_object_or_404(trackId)
	# #FIXME: the calculation of the progress is done randomly until we have a real user account management, which keeps track of actual user's progress
	nbValidatedSkill = 0
	skillList = track.skills()
	for skill in skillList:
		skillValidated = getSkillValidated(skill.id)
		if skillValidated: nbValidatedSkill += 1
	return {'current': nbValidatedSkill, 'max': len(skillList)}

# #FIXME: the calculation of the progress is done randomly until we have a real user account management, which keeps track of actual user's progress
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