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


# Curated YouTube videos: (title, youtube_video_id, bg_color, thumbnail_file)
# To add a video: go to youtube.com, find the video, copy the ID from the URL
# e.g. https://www.youtube.com/watch?v=dQw4w9WgXcQ → ID is "dQw4w9WgXcQ"
# Thumbnail: save a .jpg to assets/videos/ (any size, gets scaled to fit card)
# Videos launch via Roku YouTube app (channel 837)
VIDEOS_DATA = [
    ("Disco Fruit Party!",          "b65MoVwANq4", (255, 100, 180), "disco_fruit.jpg"),
    ("Fruit Salad Dance Party",     "wzGRs-C8kqs", (100, 200, 80),  "fruit_salad.jpg"),
    ("Dua Lipa - Houdini",         "suAR1PYFNYA", (180, 80, 220),  "houdini.jpg"),
    ("Uptown Funk - Bruno Mars",    "OPf0YbXqDm0", (220, 50, 50),   "uptown_funk.jpg"),
    ("MJ - Smooth Criminal",        "h_D3VFfhvs4", (60, 60, 60),    "smooth_criminal.jpg"),
    ("Daft Punk - Get Lucky",       "5NV6Rdv1a3I", (200, 170, 50),  "get_lucky.jpg"),
    ("Daft Punk - Get Lucky (Full)","h5EofwRzit0", (50, 180, 200),  "get_lucky_full.jpg"),
    ("Sabrina Carpenter - Espresso","eVli-tstM5E", (180, 120, 80),  "espresso.jpg"),
    ("MJ - Beat It",                "oRdxUFDoQe0", (200, 30, 30),   "beat_it.jpg"),
    ("MJ - Speed Demon",            "l039y9FaIjc", (80, 80, 180),   "speed_demon.jpg"),
    ("MJ - Leave Me Alone",         "crbFmpezO4A", (50, 150, 100),  "leave_me_alone.jpg"),
    ("MJ - Remember The Time",      "3LUQ_Vme2fo", (180, 140, 60),  "remember_the_time.jpg"),
    ("Kylie - Come Into My World",   "TOoe3EsafFk", (200, 80, 150),  "come_into_my_world.jpg"),
    ("Baa We're Lambs",             "PZKeBdYgD90", (100, 180, 100), "baa_lambs.jpg"),
    ("Walking in the Rain",         "JwaiZNbps4M", (70, 100, 160),  "walking_rain.jpg"),
    ("Beach Boys - Barbara Ann",    "4wvx14Qv9cg", (80, 180, 220),  "barbara_ann.jpg"),
    ("ROSE & Bruno Mars - APT.",    "ekr2nIex040", (220, 60, 120),  "apt.jpg"),
]
YOUTUBE_CHANNEL_ID = 837  # Roku YouTube app channel ID

# Admin shutdown — hidden 5-tap zone on main menu reveals PIN keypad
ADMIN_PIN = "0326"              # 4-digit PIN to confirm shutdown
# "quit" = exit to desktop, "shutdown" = power off the Pi
SHUTDOWN_ACTION = "quit"

# Sound hooks — uncomment and set paths when audio hardware is connected
# SOUNDS = {}
