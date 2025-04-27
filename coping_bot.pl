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
suggestion(Emotion, Stressor, Physical, Time, Support, Environment, Preference, Coping) :-
    % For severe anxiety with physical symptoms
    (Emotion = severe_anxiety, Physical \= none) ->
        (Coping = deep_breathing; Coping = progressive_muscle_relaxation);
    
    % For moderate anxiety in social situations
    (Emotion = moderate_anxiety, Environment = public) ->
        (Coping = grounding_exercises; Coping = deep_breathing);
    
    % For sadness with available support
    (member(Emotion, [mild_sadness, moderate_sadness]), Support = available) ->
        (Coping = talking_to_friend; Coping = journaling);
    
    % For overwhelming feelings in private
    (Emotion = overwhelmed, Environment = private) ->
        (Coping = meditation; Coping = journaling);
    
    % For work-related stress with active preference
    (Stressor = work, Preference = active) ->
        (Coping = exercise; Coping = time_management);
    
    % For exam stress in the evening
    (Stressor = exams, Time = evening) ->
        (Coping = progressive_muscle_relaxation; Coping = meditation);
    
    % Default suggestions based on preferences
    (Preference = active) -> Coping = exercise;
    (Preference = passive) -> Coping = meditation;
    (Preference = social) -> Coping = talking_to_friend;
    (Preference = solitary) -> Coping = journaling.

% Response Handler
respond(Emotion, Stressor, Physical, Time, Support, Environment, Preference, Suggestion) :-
    suggestion(Emotion, Stressor, Physical, Time, Support, Environment, Preference, Suggestion), !.

respond(_, _, _, _, _, _, _, 'talk_to_a_therapist').
