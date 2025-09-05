from khx_color_text import cline

print("=== Testing cline with Character Names ===\n")

# Test using character names instead of direct characters
print("1. Using character names:")
cline("asterisk", color="#FF0000")
cline("full_block", color="#00FF00")
cline("wave_dash", color="#0000FF")
cline("black_diamond", color="#FF00FF")
cline("infinity", color="#FFFF00")

print("\n2. Comparing direct chars vs names:")
print("Direct character:")
cline("*", width=30, color="#FF0000")
print("Character name:")
cline("asterisk", width=30, color="#FF0000")

print("\n3. Unicode characters by name:")
cline("double_horizontal", color="#00FFFF")
cline("heavy_horizontal", color="#FF8000")
cline("light_shade", color="#808080")
cline("medium_shade", color="#606060")
cline("dark_shade", color="#404040")

print("\n4. Mathematical symbols:")
cline("summation", width=25, color="#9370DB")
cline("integral", width=25, color="#32CD32")
cline("square_root", width=25, color="#FF69B4")

print("\n5. Geometric patterns:")
cline("black_up_triangle", width=35, color="#FF4500")
cline("black_down_triangle", width=35, color="#4169E1")
cline("black_diamond", width=35, color="#DA70D6")

print("\n6. Decorative characters:")
cline("black_star", color="#FFD700")
cline("heart_suit", color="#FF1493")
cline("diamond_suit", color="#FF6347")

print("\n=== Character Names Test Complete ===")
