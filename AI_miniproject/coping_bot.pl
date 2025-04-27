% Facts - Expanded emotional states
emotion(mild_anxiety).
emotion(moderate_anxiety).
emotion(severe_anxiety).
emotion(mild_sadness).
emotion(moderate_sadness).
emotion(severe_sadness).
emotion(overwhelmed).
emotion(angry).
emotion(frustrated).
emotion(hopeless).

% Facts - Expanded stressors
stressor(work).
stressor(exams).
stressor(relationships).
stressor(financial).
stressor(health).
stressor(family).
stressor(social).
stressor(environmental).

% Facts - Physical symptoms
physical_symptom(headache).
physical_symptom(insomnia).
physical_symptom(fatigue).
physical_symptom(tension).
physical_symptom(none).

% Facts - Time factors
time_factor(morning).
time_factor(afternoon).
time_factor(evening).
time_factor(night).

% Facts - Support system
support_system(available).
support_system(unavailable).

% Facts - Environment
environment(home).
environment(workplace).
environment(public).
environment(private).

% Facts - Personal preferences
preference(active).
preference(passive).
preference(social).
preference(solitary).

% Facts - Coping mechanisms with categories
coping(deep_breathing, relaxation).
coping(progressive_muscle_relaxation, relaxation).
coping(meditation, mindfulness).
coping(grounding_exercises, mindfulness).
coping(journaling, emotional_expression).
coping(art_therapy, emotional_expression).
coping(exercise, physical_activity).
coping(yoga, physical_activity).
coping(talking_to_friend, social_support).
coping(professional_help, social_support).
coping(time_management, practical).
coping(problem_solving, practical).

% Rules for suggesting coping mechanisms based on multiple factors
suggest_coping(severe_anxiety, _, Physical, _, _, _, [deep_breathing, progressive_muscle_relaxation]) :-
    Physical \= none.

suggest_coping(moderate_anxiety, _, _, _, _, public, [grounding_exercises, deep_breathing]).

suggest_coping(Emotion, _, _, _, available, _, [talking_to_friend, journaling]) :-
    member(Emotion, [mild_sadness, moderate_sadness]).

suggest_coping(overwhelmed, _, _, _, _, private, [meditation, journaling]).

suggest_coping(_, work, _, _, _, _, [time_management, exercise]).

suggest_coping(_, exams, _, evening, _, _, [progressive_muscle_relaxation, meditation]).

suggest_coping(_, _, Physical, _, _, _, [deep_breathing, progressive_muscle_relaxation]) :-
    Physical \= none.

suggest_coping(_, _, _, _, available, public, [talking_to_friend, grounding_exercises]).

suggest_coping(_, _, _, morning, _, _, [exercise, meditation]).

suggest_coping(_, _, _, night, _, _, [progressive_muscle_relaxation, journaling]).

% Default case - if no other rules match
suggest_coping(_, _, _, _, _, _, [deep_breathing, journaling]).

% Response Handler
respond(Emotion, Stressor, Physical, Time, Support, Environment, Suggestions) :-
    suggest_coping(Emotion, Stressor, Physical, Time, Support, Environment, Suggestions),
    write(Suggestions), nl, !.

respond(_, _, _, _, _, _, [deep_breathing, 'talk_to_a_therapist']) :-
    write([deep_breathing, 'talk_to_a_therapist']), nl.
