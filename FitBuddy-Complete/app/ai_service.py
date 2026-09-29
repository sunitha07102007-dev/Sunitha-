import json
from typing import Any
from google import genai
from google.genai import types
from .config import settings

SYSTEM = """You are FitBuddy, a conservative fitness-planning assistant. Generate practical beginner-friendly plans. Do not diagnose disease, prescribe treatment, or encourage unsafe rapid weight loss. Include a brief safety note when relevant. Never claim the plan is a substitute for a qualified healthcare professional."""

class AIService:
    def __init__(self):
        self.client = genai.Client(api_key=settings.gemini_api_key) if settings.gemini_api_key else None

    def _generate(self, model: str, prompt: str) -> str:
        if not self.client:
            raise RuntimeError("Gemini API key is not configured")
        response = self.client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM,
                temperature=settings.model_temperature,
                max_output_tokens=settings.model_max_tokens,
            ),
        )
        text = getattr(response, "text", None)
        if not text:
            raise RuntimeError("Gemini returned an empty response")
        return text.strip()

    def workout(self, data: Any) -> str:
        prompt = f"""Create a personalized 7-day workout plan for:
Name: {data.name}
Age: {data.age}
Weight: {data.weight} kg
Goal: {data.goal}
Intensity: {data.intensity}

Format exactly as Day 1 through Day 7. For each day include Focus, Warm-up, Main workout with sets/reps or duration, Rest, and Cool-down/Recovery. Include at least one recovery/rest-focused day. Keep the plan realistic and avoid unsupported medical claims."""
        return self._generate(settings.workout_model, prompt)

    def nutrition(self, data: Any) -> str:
        prompt = f"Give one concise nutrition or recovery tip for a person whose fitness goal is {data.goal}. Mention one or two practical food/hydration/recovery actions. Avoid calorie prescriptions and medical advice. Maximum 100 words."
        return self._generate(settings.nutrition_model, prompt)

    def update(self, data: Any, original_plan: str, feedback: str) -> str:
        prompt = f"""Revise this 7-day workout plan based on the user's feedback.
User profile: age={data.age}, weight={data.weight} kg, goal={data.goal}, intensity={data.intensity}.
Original plan:
{original_plan}

User feedback:
{feedback}

Return a complete revised Day 1-Day 7 plan, preserving useful parts and applying the requested changes. Include warm-up, main workout, rest, and cool-down/recovery for each day."""
        return self._generate(settings.workout_model, prompt)

    def safe_call(self, method, *args):
        try:
            return method(*args), False
        except Exception:
            if not settings.model_fallback_to_demo:
                raise
            return None, True

ai = AIService()

def demo_workout(data):
    focus = {"weight loss":"cardio + full body", "muscle gain":"strength", "general wellness":"full body wellness", "flexibility":"mobility + flexibility", "endurance":"cardio endurance"}[data.goal]
    return f"""DAY 1 — Full Body Foundation\nFocus: {focus}\nWarm-up: 7 min brisk walk + mobility\nMain: Squats 3x10, Incline push-ups 3x8, Glute bridges 3x12, Plank 3x20 sec\nRest: 60–90 sec between sets\nCool-down: 5 min easy stretching\n\nDAY 2 — Cardio & Core\nWarm-up: 5–7 min easy movement\nMain: Brisk walk/jog 20 min, Dead bug 3x10/side, Bird dog 3x10/side\nRest: 60 sec\nCool-down: 5 min\n\nDAY 3 — Recovery\nFocus: Active recovery\nWarm-up: 5 min easy walk\nMain: Gentle mobility or yoga 20–30 min\nRest: Keep intensity comfortable\nCool-down: Relaxed breathing + stretching\n\nDAY 4 — Lower Body\nWarm-up: 7 min\nMain: Squats 3x10, Reverse lunges 3x8/side, Calf raises 3x15, Glute bridges 3x12\nRest: 60–90 sec\nCool-down: 5 min\n\nDAY 5 — Upper Body & Core\nWarm-up: 7 min\nMain: Incline push-ups 3x8, Band/towel rows 3x10, Shoulder taps 3x10/side, Plank 3x20 sec\nRest: 60–90 sec\nCool-down: 5 min\n\nDAY 6 — Cardio\nWarm-up: 5–7 min\nMain: Brisk walk/cycle 25–30 min at {data.intensity} effort\nRest: Take short breaks as needed\nCool-down: 5 min easy walk\n\nDAY 7 — Rest & Mobility\nFocus: Recovery\nMain: Optional gentle walk 15–20 min + full-body mobility\nCool-down: Easy stretching\n\nSafety: Stop if you feel sharp pain, dizziness, or unusual shortness of breath. Adjust difficulty to your current fitness level."""

def demo_tip(data):
    tips = {
        "weight loss":"Build meals around vegetables, a protein source, whole grains or other high-fiber foods, and water. Consistency matters more than extreme restriction.",
        "muscle gain":"Include a protein-rich food in regular meals and prioritize sleep and recovery alongside resistance training.",
        "general wellness":"Stay hydrated, eat a varied diet with fruits and vegetables, and keep a consistent sleep routine.",
        "flexibility":"Hydrate normally and pair mobility sessions with balanced meals and adequate recovery.",
        "endurance":"Prioritize fluids and carbohydrate-rich foods around longer sessions, while keeping regular balanced meals."
    }
    return tips[data.goal]
