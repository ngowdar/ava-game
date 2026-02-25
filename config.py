# config.py — Constants for Ava's Game Box

# Display
WIDTH = 720
HEIGHT = 720
FPS = 60

# Roku
ROKU_IP = "10.0.0.60"
ROKU_PORT = 8060

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SKY_BLUE = (135, 206, 235)
GOLD = (255, 215, 0)
GREEN = (76, 175, 80)
ORANGE = (255, 152, 0)
DARK_GRAY = (60, 60, 60)
LIGHT_GRAY = (180, 180, 180)

# States
MAIN_MENU = "MAIN_MENU"
GAMES_MENU = "GAMES_MENU"
FINGER_PAINT = "FINGER_PAINT"
SHAPE_SORTER = "SHAPE_SORTER"
MAGIC_GARDEN = "MAGIC_GARDEN"
FIREWORKS = "FIREWORKS"
PARTICLE_PLAYGROUND = "PARTICLE_PLAYGROUND"
WEATHER_TOY = "WEATHER_TOY"
SHOWS = "SHOWS"
REMOTE = "REMOTE"
VIDEOS = "VIDEOS"

# Back button
BACK_BTN_SIZE = 80
BACK_BTN_MARGIN = 15

# Show data: (name, channel_id, content_id, media_type, bg_color, image_file or None)
SHOWS_DATA = [
    ("Bluey",           291097, "fa6973b9-e7cf-49fb-81a2-d4908e4bf694", "series", (0, 150, 255),   "bluey.png"),
    ("Little Mermaid",  291097, "f7643452-fe64-4b05-8f09-c8bea9b2dd60", "movie",  (0, 190, 210),   "little_mermaid.png"),
    ("Frozen",          291097, "04c97b72-504b-47f2-9c6f-fe13d9aea82f", "movie",  (130, 200, 245), "frozen.png"),
    ("Aladdin",         291097, "bfad6284-a0aa-4ae1-8469-dc1653121dbb", "movie",  (100, 50, 150),  "aladdin.png"),
    ("Lion King",       291097, "87524f44-a8ea-4b08-b4d8-39103bed3eaa", "movie",  (255, 180, 60),  "lion_king.png"),
    ("K-Pop Demon H.",  12,     "81498621",                              "movie",  (255, 50, 130),  "kpop.png"),
    ("Moana",           291097, "e8896bfa-1052-41f7-ae2e-00255d77cf05", "movie",  (0, 160, 180),   "moana.png"),
    ("Princess & Frog", 291097, "2349fffc-2124-4eca-b5e5-a8bb97e569c4", "movie",  (0, 160, 80),    "princess_frog.png"),
    ("Elmo",            61322,  "f175ce7b-ab72-4ac9-a029-c8c29bd17b7c", "series", (220, 30, 30),   "elmo.png"),
    ("Ms. Rachel",      12,     "81975233",                              "series", (255, 180, 220), "ms_rachel.png"),
    ("Wall-E",          291097, "280395a4-d5ef-4dd0-bd09-d91c31593d3d", "movie",  (139, 90, 43),   None),
    ("Toy Story",       291097, "f6174ebf-cb92-453c-a52b-62bb3576e402", "movie",  (0, 130, 200),   None),
    ("Tarzan",          291097, "6246ebb7-7e52-4767-974c-5da108c6644f", "movie",  (34, 120, 15),   None),
]


# Curated YouTube videos: (title, youtube_video_id, bg_color)
# To add a video: go to youtube.com, find the video, copy the ID from the URL
# e.g. https://www.youtube.com/watch?v=dQw4w9WgXcQ → ID is "dQw4w9WgXcQ"
VIDEOS_DATA = [
    # Add your curated videos here! Examples:
    # ("Baby Shark",      "XqZsoesa55w", (255, 200, 50)),
    # ("Wheels on the Bus","e_04ZrNroTo", (80, 180, 255)),
    # ("Old MacDonald",   "5oYGFnFKkBE", (100, 200, 80)),
]

# Sound hooks — uncomment and set paths when audio hardware is connected
# SOUNDS = {}
