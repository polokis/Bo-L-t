import discord
from discord.ext import commands, tasks
import asyncio
import os
from datetime import datetime
import logging
from scraper import RTanksPlayerScraper
from translator import RTanksTranslator
from config import RANK_EMOJIS, LEADERBOARD_CATEGORIES

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot setup with required intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Initialize scraper and translator
scraper = RTanksPlayerScraper()
translator = RTanksTranslator()

# Global variables for configuration
LEADERBOARD_CHANNEL_ID = int(os.getenv('LEADERBOARD_CHANNEL_ID', '0'))

@bot.event
async def on_ready():
    logger.info(f'{bot.user} has connected to Discord!')
    logger.info(f'Bot ID: {bot.user.id}')
    logger.info(f'Bot is in {len(bot.guilds)} guilds')
    
    # Wait a moment before syncing
    await asyncio.sleep(1)
    
    # Sync slash commands globally
    try:
        logger.info("Starting command sync...")
        # Add timeout to prevent hanging
        synced = await asyncio.wait_for(bot.tree.sync(), timeout=30.0)
        logger.info(f"Successfully synced {len(synced)} global command(s)")
        for cmd in synced:
            logger.info(f"Synced command: {cmd.name} - {cmd.description}")
    except asyncio.TimeoutError:
        logger.error("Command sync timed out - this usually means the bot lacks 'applications.commands' scope")
        logger.error("Please re-invite the bot with both 'bot' and 'applications.commands' scopes")
    except discord.Forbidden:
        logger.error("Bot lacks permissions to register slash commands")
        logger.error("Please re-invite the bot with 'applications.commands' scope")
    except Exception as e:
        logger.error(f"Failed to sync global commands: {e}")
        logger.error(f"Error type: {type(e).__name__}")
    
    # List current commands in tree
    logger.info(f"Commands in tree: {[cmd.name for cmd in bot.tree.get_commands()]}")
    
    # Start hourly leaderboard task
    if not hourly_leaderboard.is_running():
        hourly_leaderboard.start()

def get_rank_emoji(rank_name: str) -> str:
    """Get the appropriate emoji for a rank name"""
    # Translate rank name to English if needed
    translated_rank = translator.translate_rank(rank_name)
    
    # Log for debugging if needed
    # logger.debug(f"Original rank: '{rank_name}' -> Translated: '{translated_rank}'")
    
    # Always try lowercase first since our emoji keys are lowercase
    lowercase_rank = translated_rank.lower()
    
    if lowercase_rank in RANK_EMOJIS:
        return RANK_EMOJIS[lowercase_rank]
    else:
        # Try to find a partial match
        for rank_key in RANK_EMOJIS.keys():
            if lowercase_rank in rank_key or rank_key in lowercase_rank:
                return RANK_EMOJIS[rank_key]
        
        # If no match found, return question mark
        return "❓"

def create_player_embed(player_data: dict) -> discord.Embed:
    """Create a Discord embed for player statistics"""
    
    # Get rank emoji
    rank_emoji = get_rank_emoji(player_data.get('rank', ''))
    
    # Create embed with player info
    embed = discord.Embed(
        title=f"{rank_emoji} {player_data['nickname']}",
        description=f"{translator.translate_text(player_data.get('rank', 'Unknown Rank'))}",
        color=0x00ff00,
        timestamp=datetime.utcnow()
    )
    
    # Main statistics section
    embed.add_field(
        name="⭐ Experience", 
        value=f"{player_data.get('experience', 'N/A'):,}", 
        inline=True
    )
    
    embed.add_field(
        name="💎 Crystals Position", 
        value=f"#{player_data.get('crystals_rank', 'N/A')}" if player_data.get('crystals_rank', 'N/A') != 'N/A' else 'N/A', 
        inline=True
    )
    
    embed.add_field(
        name="⚔️ Kills", 
        value=f"{player_data.get('kills', 'N/A'):,}", 
        inline=True
    )
    
    embed.add_field(
        name="💀 Deaths", 
        value=f"{player_data.get('deaths', 'N/A'):,}", 
        inline=True
    )
    
    embed.add_field(
        name="📊 K/D Ratio", 
        value=f"{player_data.get('kd_ratio', 'N/A')}", 
        inline=True
    )
    
    embed.add_field(
        name="🏆 Efficiency Rank", 
        value=f"#{player_data.get('efficiency_rank', 'N/A')}" if player_data.get('efficiency_rank', 'N/A') != 'N/A' else 'N/A', 
        inline=True
    )
    
    # Add premium status
    premium_emoji = "👑" if player_data.get('premium') else "❌"
    embed.add_field(
        name="💳 Premium Status", 
        value=f"{premium_emoji} {'Premium' if player_data.get('premium') else 'Free'}", 
        inline=True
    )
    
    # Add goldboxes with emoji
    from config import GOLDBOX_EMOJI
    embed.add_field(
        name=f"{GOLDBOX_EMOJI} Gold Boxes", 
        value=f"{player_data.get('goldboxes', 'N/A')}", 
        inline=True
    )
    
    # Add group/player type
    embed.add_field(
        name="👥 Group", 
        value="Player", 
        inline=True
    )
    
    # Add current rankings section (translate to English)
    rankings_data = []
    if player_data.get('experience_rank') and player_data.get('experience_rank') != 'N/A':
        rankings_data.append(f"By experience: #{player_data.get('experience_rank')}")
    if player_data.get('crystals_rank') and player_data.get('crystals_rank') != 'N/A':
        rankings_data.append(f"By crystals: #{player_data.get('crystals_rank')}")
    if player_data.get('kills_rank') and player_data.get('kills_rank') != 'N/A':
        rankings_data.append(f"By kills: #{player_data.get('kills_rank')}")
    if player_data.get('efficiency_rank') and player_data.get('efficiency_rank') != 'N/A':
        rankings_data.append(f"By efficiency: #{player_data.get('efficiency_rank')}")
    
    if rankings_data:
        embed.add_field(
            name="🏆 Current Rankings", 
            value="\n".join(rankings_data), 
            inline=False
        )
    
    # Add equipment info if available
    if player_data.get('equipment'):
        equipment_text = translator.translate_text(player_data['equipment'])
        embed.add_field(
            name="🛡️ Current Equipment", 
            value=equipment_text, 
            inline=False
        )
    
    embed.set_footer(text="RTanks Online Statistics", icon_url="https://ratings.ranked-rtanks.online/public/images/logo.png")
    
    return embed

@bot.tree.command(name="player", description="Get RTanks Online player statistics")
@discord.app_commands.describe(nickname="The player's nickname to look up")
async def player_stats(interaction: discord.Interaction, nickname: str):
    """Slash command to get player statistics"""
    
    # Defer the response since scraping might take time
    await interaction.response.defer()
    
    try:
        # Scrape player data
        player_data = await scraper.get_player_stats(nickname)
        
        # Debug log the extracted data
        if player_data:
            logger.info(f"Player data for {nickname}: Experience={player_data.get('experience')}, Kills={player_data.get('kills')}, Deaths={player_data.get('deaths')}, K/D={player_data.get('kd_ratio')}")
        
        if not player_data:
            embed = discord.Embed(
                title="❌ Player Not Found",
                description=f"No player found with nickname: **{nickname}**",
                color=0xff0000
            )
            embed.add_field(
                name="💡 Tip", 
                value="Make sure the nickname is spelled correctly and the player exists in RTanks Online.",
                inline=False
            )
            await interaction.followup.send(embed=embed)
            return
        
        # Create and send embed
        embed = create_player_embed(player_data)
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        logger.error(f"Error fetching player stats for {nickname}: {e}")
        
        embed = discord.Embed(
            title="⚠️ Error",
            description="Failed to retrieve player statistics. This could be due to:",
            color=0xffa500
        )
        embed.add_field(
            name="Possible Causes", 
            value="• RTanks website is temporarily unavailable\n• Network connection issues\n• Player profile is private or restricted",
            inline=False
        )
        embed.add_field(
            name="Try Again", 
            value="Please try again in a few moments. If the issue persists, the RTanks website may be experiencing downtime.",
            inline=False
        )
        
        await interaction.followup.send(embed=embed)

class LeaderboardView(discord.ui.View):
    """View for leaderboard category selection"""
    
    def __init__(self):
        super().__init__(timeout=60)
    
    @discord.ui.select(
        placeholder="Choose a leaderboard category...",
        options=[
            discord.SelectOption(
                label="Experience Leaderboard",
                description="Top players by earned experience",
                value="experience",
                emoji="📊"
            ),
            discord.SelectOption(
                label="Crystals Leaderboard", 
                description="Top players by earned crystals",
                value="crystals",
                emoji="💎"
            ),
            discord.SelectOption(
                label="Kills Leaderboard",
                description="Top players by total kills",
                value="kills", 
                emoji="⚔️"
            ),
            discord.SelectOption(
                label="Efficiency Leaderboard",
                description="Top players by efficiency rating",
                value="efficiency",
                emoji="🏆"
            )
        ]
    )
    async def select_leaderboard(self, interaction: discord.Interaction, select: discord.ui.Select):
        await interaction.response.defer()
        
        try:
            category = select.values[0]
            leaderboard_data = await scraper.get_leaderboard(category)
            
            if not leaderboard_data:
                embed = discord.Embed(
                    title="❌ Leaderboard Unavailable",
                    description=f"Could not retrieve {category} leaderboard data.",
                    color=0xff0000
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Create leaderboard embed
            embed = create_leaderboard_embed(leaderboard_data, category)
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error fetching leaderboard for {select.values[0]}: {e}")
            
            embed = discord.Embed(
                title="⚠️ Error",
                description="Failed to retrieve leaderboard data.",
                color=0xffa500
            )
            await interaction.followup.send(embed=embed)

def create_leaderboard_embed(leaderboard_data: list, category: str) -> discord.Embed:
    """Create a Discord embed for leaderboard data"""
    
    category_info = LEADERBOARD_CATEGORIES.get(category, {})
    title = category_info.get('title', f'{category.title()} Leaderboard')
    emoji = category_info.get('emoji', '🏆')
    
    embed = discord.Embed(
        title=f"{emoji} {title}",
        description=f"Top 10 players in RTanks Online",
        color=0x00ff00,
        timestamp=datetime.utcnow()
    )
    
    # Add top 10 players to avoid Discord's 1024 character limit
    leaderboard_text = ""
    for i, player in enumerate(leaderboard_data[:10], 1):
        rank_emoji = get_rank_emoji(player.get('rank', ''))
        
        # Format position with medals for top 3
        if i == 1:
            position = "🥇"
        elif i == 2:
            position = "🥈" 
        elif i == 3:
            position = "🥉"
        else:
            position = f"{i}."
        
        value = player.get('value', 'N/A')
        if isinstance(value, (int, float)) and value >= 1000:
            value = f"{value:,}"
        
        # Truncate long nicknames to prevent field overflow
        nickname = player['nickname']
        if len(nickname) > 15:
            nickname = nickname[:12] + "..."
        
        leaderboard_text += f"{position} {rank_emoji} **{nickname}** - {value}\n"
    
    # Split into multiple fields if still too long
    if len(leaderboard_text) > 1000:
        # Split into two fields
        lines = leaderboard_text.strip().split('\n')
        mid_point = len(lines) // 2
        
        embed.add_field(
            name="Rankings (1-5)", 
            value='\n'.join(lines[:mid_point]) or "No data available",
            inline=True
        )
        embed.add_field(
            name="Rankings (6-10)", 
            value='\n'.join(lines[mid_point:]) or "No data available",
            inline=True
        )
    else:
        embed.add_field(
            name="Top 10 Rankings", 
            value=leaderboard_text or "No data available",
            inline=False
        )
    
    embed.set_footer(
        text="RTanks Online Leaderboard • Updates weekly", 
        icon_url="https://ratings.ranked-rtanks.online/public/images/logo.png"
    )
    
    return embed

@bot.tree.command(name="top", description="View RTanks Online leaderboards")
async def leaderboard(interaction: discord.Interaction):
    """Slash command to show leaderboard selection"""
    
    embed = discord.Embed(
        title="🏆 RTanks Online Leaderboards",
        description="Select a category to view the top players:",
        color=0x00ff00
    )
    
    view = LeaderboardView()
    await interaction.response.send_message(embed=embed, view=view)

@tasks.loop(hours=1)
async def hourly_leaderboard():
    """Post leaderboards to designated channel every hour"""
    
    if LEADERBOARD_CHANNEL_ID == 0:
        logger.warning("No leaderboard channel configured")
        return
    
    channel = bot.get_channel(LEADERBOARD_CHANNEL_ID)
    if not channel:
        logger.error(f"Could not find channel with ID {LEADERBOARD_CHANNEL_ID}")
        return
    
    try:
        # Post all leaderboard categories
        for category_key, category_info in LEADERBOARD_CATEGORIES.items():
            try:
                leaderboard_data = await scraper.get_leaderboard(category_key)
                
                if leaderboard_data:
                    embed = create_leaderboard_embed(leaderboard_data, category_key)
                    await channel.send(embed=embed)
                
                # Small delay between posts
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"Error posting {category_key} leaderboard: {e}")
        
        logger.info("Hourly leaderboards posted successfully")
        
    except Exception as e:
        logger.error(f"Error in hourly leaderboard task: {e}")

@hourly_leaderboard.before_loop
async def before_hourly_leaderboard():
    """Wait for bot to be ready before starting the loop"""
    await bot.wait_until_ready()

# Error handling for commands
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
    """Global error handler for slash commands"""
    
    logger.error(f"Command error: {error}")
    
    embed = discord.Embed(
        title="⚠️ Command Error",
        description="An unexpected error occurred while processing your command.",
        color=0xff0000
    )
    
    if interaction.response.is_done():
        await interaction.followup.send(embed=embed, ephemeral=True)
    else:
        await interaction.response.send_message(embed=embed, ephemeral=True)

# Run the bot
from keep_alive import keep_alive

if __name__ == "__main__":
    token = os.getenv('DISCORD_BOT_TOKEN')
    if not token:
        logger.error("DISCORD_BOT_TOKEN environment variable is required")
        exit(1)

    keep_alive()  # Prevents bot from sleeping on Render
    bot.run(token)

