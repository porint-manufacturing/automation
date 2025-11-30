import uiautomation as auto

print("--- uiautomation Properties ---")
for prop in dir(auto):
    if "Time" in prop or "Delay" in prop or "Speed" in prop:
        print(f"{prop}: {getattr(auto, prop)}")
