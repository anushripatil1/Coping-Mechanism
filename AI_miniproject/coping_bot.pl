% Facts
stressor(work).
stressor(exams).
stressor(relationships).

emotion(anxious).
emotion(sad).
emotion(overwhelmed).

coping(deep_breathing).
coping(journaling).
coping(talking_to_someone).

% Rules
suggestion(anxious, work, deep_breathing).
suggestion(sad, relationships, journaling).
suggestion(overwhelmed, exams, talking_to_someone).

% Response Handler
respond(Emotion, Stressor, Suggestion) :-
    suggestion(Emotion, Stressor, Suggestion), !.

respond(_, _, 'talk_to_a_therapist').
