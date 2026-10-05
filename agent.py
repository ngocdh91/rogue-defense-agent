import json
import ollama

# 1. Đồng bộ danh sách ưu tiên chuẩn (1 đến 8)
PRIORITY_ORDER = [
    "Electro",    # Rank 1
    "Bullet",     # Rank 2
    "Field",      # Rank 3
    "Traction",   # Rank 4
    "Laser",      # Rank 5
    "Thunder",    # Rank 6
    "FireWheel",  # Rank 7
    "Mortar"      # Rank 8
]

class RogueAgent:
    def __init__(self, model_name="qwen2.5-coder"):
        self.model_name = model_name

    def _get_python_best_choice(self, available_skills):
        """Hàm thuần Python xác định skill tốt nhất để làm chuẩn đối chiếu."""
        # Lọc bỏ EliteAd
        valid_skills = [s for s in available_skills if s.get("class") != "EliteAd"]
        if not valid_skills:
            return available_skills[0]

        # Tìm skill có thứ tự ưu tiên cao nhất trong PRIORITY_ORDER
        for prio in PRIORITY_ORDER:
            for skill in valid_skills:
                if skill.get("class") == prio:
                    return skill

        return valid_skills[0]

    def choose_skill(self, available_skills):
        """
        Gửi yêu cầu tới Ollama, kèm theo bộ kiểm định (Validator) để tránh LLM ảo giác.
        """
        # Đánh dấu vị trí (index) cụ thể cho từng thẻ
        skills_summary = [
            {"index": idx, "class": item["class"]} 
            for idx, item in enumerate(available_skills)
        ]

        # Prompt đồng bộ hoàn toàn với PRIORITY_ORDER
        prompt = f"""You are an AI assistant playing a game. Pick ONE skill index from the provided list based strictly on the priority table.

AVAILABLE SKILLS ON SCREEN:
{json.dumps(skills_summary, indent=2)}

PRIORITY RANKING (1 is Highest, 8 is Lowest):
1. Electro
2. Bullet
3. Field
4. Traction
5. Laser
6. Thunder
7. FireWheel
8. Mortar

STRICT RULES:
- Compare the available skills using the PRIORITY RANKING above.
- Always choose the skill with the highest rank (closest to 1).
- Example: If 'Electro' and 'Bullet' are available, you MUST pick 'Electro' because Electro (Rank 1) > Bullet (Rank 2).
- Never select 'EliteAd'.

Return ONLY a JSON object:
{{
  "chosen_index": <int_0_or_1_or_2>,
  "chosen_skill": "<skill_name>",
  "reason": "<short_explanation>"
}}
"""

        best_python_choice = self._get_python_best_choice(available_skills)

        try:
            response = ollama.chat(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                format="json"
            )
            content = response['message']['content']
            result = json.loads(content)

            chosen_index = result.get("chosen_index")
            reason = result.get("reason", "")

            # Kiểm tra xem chosen_index có phải kiểu số nguyên hợp lệ không
            if isinstance(chosen_index, int) and 0 <= chosen_index < len(available_skills):
                ai_selected = available_skills[chosen_index]

                # 🛑 BƯỚC KIỂM ĐỊNH (VALIDATION): Nếu AI chọn sai so với logic ưu tiên
                if ai_selected["class"] != best_python_choice["class"]:
                    ai_prio = PRIORITY_ORDER.index(ai_selected["class"]) if ai_selected["class"] in PRIORITY_ORDER else 99
                    best_prio = PRIORITY_ORDER.index(best_python_choice["class"]) if best_python_choice["class"] in PRIORITY_ORDER else 99

                    if ai_prio > best_prio:
                        # Lấy index thực tế của best_python_choice trong available_skills
                        best_index = available_skills.index(best_python_choice)
                        print(f"[AI AGENT ⚠️] Ollama ảo giác khi chọn '{ai_selected['class']}' (Index {chosen_index}). Ghi đè sang '{best_python_choice['class']}' (Index {best_index})!")
                        return best_python_choice

                print(f"[AI AGENT] 🧠 Ollama chọn Index [{chosen_index}] - Skill: {ai_selected['class']} | Lý do: {reason}")
                return ai_selected

            print("[AI AGENT ⚠️] Index trả về không hợp lệ. Dùng kết quả Python Validator.")
            return best_python_choice

        except Exception as e:
            print(f"[AI AGENT LỖI] {e}. Dùng kết quả Python Validator.")
            return best_python_choice