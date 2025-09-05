from khx_color_text import cline

# Test the cline function with different parameters
print("=== Testing cline function ===\n")

# Basic line filling terminal width
print("1. Basic line (fills terminal):")
cline()

print("\n2. Custom character and color:")
cline("*", color="#FF0000")

print("\n3. Fixed width line:")
cline("=", width=30, color="blue", style="bold")

print("\n4. Block line with background:")
cline("█", color="#FFFFFF", bg_color="#FF0000")

print("\n5. Wave line:")
cline("~", color="#00FFFF", style="italic")

print("\n6. Double line:")
cline("═", color="#FFD700")

print("\n7. Decorative diamond line:")
cline("◆", width=40, color="#FF69B4")

print("\n8. Mathematical symbols:")
cline("∞", width=25, color="#9370DB")

print("\n9. Geometric pattern:")
cline("▲", width=35, color="#32CD32")

print("\n10. Mixed style:")
cline("★", color="#FF4500", bg_color="#000080", style=["bold", "underline"])

print("\n=== End of tests ===")
