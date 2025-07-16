"""Configuration settings for the RTanks Discord Bot"""

# Rank emoji mappings (emoji_1 to emoji_31)
# Using the actual Discord emoji IDs provided by the user
RANK_EMOJIS = {
    'recruit': '<:emoji_1:1394987021415743588>',
    'private': '<:emoji_2:1394987069088206929>',
    'private first class': '<:emoji_3:1394987101941923930>',
    'lance corporal': '<:emoji_4:1394987134980587630>',
    'corporal': '<:emoji_5:1394987177284468767>',
    'sergeant': '<:emoji_6:1394987207583989830>',
    'staff sergeant': '<:emoji_7:1394987243629969581>',
    'sergeant first class': '<:emoji_8:1394987270146097202>',
    'master sergeant': '<:emoji_9:1394987302379458591>',
    'warrant officer 1': '<:emoji_10:1394987333488480256>',
    'warrant officer 2': '<:emoji_11:1394987701048049726>',
    'warrant officer 3': '<:emoji_12:1394987730722754641>',
    'warrant officer 4': '<:emoji_13:1394987756412866632>',
    'warrant officer 5': '<:emoji_14:1394987853104156823>',
    'second lieutenant': '<:emoji_15:1394987883760324631>',
    'first lieutenant': '<:emoji_16:1394988524285198356>',
    'captain': '<:emoji_17:1394988592517873775>',
    'major': '<:emoji_18:1394988631609049169>',
    'lieutenant colonel': '<:emoji_19:1394988655252078743>',
    'colonel': '<:emoji_20:1394988771665248286>',
    'brigadier general': '<:emoji_21:1394988797569142845>',
    'major general': '<:emoji_22:1394988842557112331>',
    'lieutenant general': '<:emoji_23:1394988970110222387>',
    'general': '<:emoji_24:1394989066667425842>',
    'generalissimo': '<:emoji_25:1394989098200207410>',
    'marshal': '<:emoji_26:1394989131364565053>',
    'field marshal': '<:emoji_27:1394989164709019708>',
    'grand marshal': '<:emoji_28:1394989205662339082>',
    'supreme commander': '<:emoji_29:1394989245978116217>',
    'overlord': '<:emoji_30:1394989278005559378>',
    'legend': '<:emoji_31:1394989379642064948>',
}

# Goldbox emoji (emoji_32)
GOLDBOX_EMOJI = '<:emoji_32:1395002503472484352>'

# Leaderboard categories configuration
LEADERBOARD_CATEGORIES = {
    'experience': {
        'title': 'Experience Leaderboard',
        'emoji': '📊',
        'description': 'Top players by earned experience points'
    },
    'crystals': {
        'title': 'Crystals Leaderboard', 
        'emoji': '💎',
        'description': 'Top players by earned crystals'
    },
    'kills': {
        'title': 'Kills Leaderboard',
        'emoji': '⚔️',
        'description': 'Top players by total eliminations'
    },
    'efficiency': {
        'title': 'Efficiency Leaderboard',
        'emoji': '🏆',
        'description': 'Top players by efficiency rating'
    }
}

# Bot configuration
BOT_CONFIG = {
    'command_prefix': '!',
    'description': 'RTanks Online Statistics Bot',
    'activity_name': 'RTanks Online',
    'activity_type': 'watching',  # watching, playing, listening, streaming
    'status': 'online'  # online, idle, dnd, invisible
}

# Scraping configuration
SCRAPER_CONFIG = {
    'base_url': 'https://ratings.ranked-rtanks.online',
    'timeout': 30,
    'max_retries': 3,
    'retry_delay': 2,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Cache configuration
CACHE_CONFIG = {
    'player_cache_ttl': 300,  # 5 minutes
    'leaderboard_cache_ttl': 900,  # 15 minutes
    'translation_cache_ttl': 3600,  # 1 hour
    'max_cache_size': 1000
}

# Error messages
ERROR_MESSAGES = {
    'player_not_found': {
        'title': '❌ Player Not Found',
        'description': 'No player found with that nickname.',
        'color': 0xff0000
    },
    'scraping_error': {
        'title': '⚠️ Website Error',
        'description': 'Unable to retrieve data from RTanks website.',
        'color': 0xffa500
    },
    'general_error': {
        'title': '❌ Error',
        'description': 'An unexpected error occurred.',
        'color': 0xff0000
    },
    'network_error': {
        'title': '🌐 Network Error',
        'description': 'Network connection failed. Please try again.',
        'color': 0xff6600
    }
}

# Success colors
EMBED_COLORS = {
    'success': 0x00ff00,
    'info': 0x00aaff,
    'warning': 0xffaa00,
    'error': 0xff0000,
    'leaderboard': 0x00ff00,
    'player_stats': 0x00ff00
}

# Rate limiting
RATE_LIMITS = {
    'requests_per_minute': 30,
    'requests_per_hour': 1000,
    'player_lookup_cooldown': 5,  # seconds
    'leaderboard_cooldown': 10  # seconds
}

# Logging configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': 'rtanks_bot.log',
    'max_size': 10 * 1024 * 1024,  # 10MB
    'backup_count': 5
}
