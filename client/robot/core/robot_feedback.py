def decide_action(data):
    score = data.get('score', 0)
    exercise = data.get('exercise', "")
    if score >= 85:
        return exercise, "Good job"
    if score >= 60:
        return exercise, "Raise higher please"
    return "stretch", "Please try again"