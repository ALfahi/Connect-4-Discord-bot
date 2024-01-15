import discord
from discord.ext import commands

class Game:# creating a game class so it's easier to create and run multiple games at once
    current_game_id = 1

    def __init__(self, player1):
        self.game_id = Game.current_game_id
        Game.current_game_id += 1
        self.p1 = True
        self.player1 = player1
        self.player2 = None
        self.win = False
        self.draw = False
        self.table = [
            ["┃", "⚫", "⚫", "⚫", "⚫", "⚫", "⚫", "⚫", "┃"],
            ["┃", "⚫", "⚫", "⚫", "⚫", "⚫", "⚫", "⚫", "┃"],
            ["┃", "⚫", "⚫", "⚫", "⚫", "⚫", "⚫", "⚫", "┃"],
            ["┃", "⚫", "⚫", "⚫", "⚫", "⚫", "⚫", "⚫", "┃"],
            ["┃", "⚫", "⚫", "⚫", "⚫", "⚫", "⚫", "⚫", "┃"],
            ["┃", "⚫", "⚫", "⚫", "⚫", "⚫", "⚫", "⚫", "┃"]
        ]

    def check_draw(self):
        if self.table[0].count("⚫") == 0:# only need to check the very top row to see if there is any empty spaces.
            self.draw = True

    def check_win(self, x_pos, y_pos):
        token = self.table[y_pos][x_pos]
        count = 0

        # Check vertical
        for i in range(4):
            if y_pos + i < len(self.table) and self.table[y_pos + i][x_pos] == token:
                count += 1
                if count >= 4:
                    self.win = True
                    return

        # Check horizontal
        count = 0
        for i in range(4):
            if 0 <= x_pos - i < len(self.table[y_pos]) and self.table[y_pos][x_pos - i] == token:
                count += 1
            else:
                break

        for i in range(1, 4):
            if 0 <= x_pos + i < len(self.table[y_pos]) and self.table[y_pos][x_pos + i] == token:
                count += 1
            else:
                break

        if count >= 4:
            self.win = True
            return

        # Check diagonal bottom left to top right
        count = 0
        for i in range(4):
            if y_pos + i < len(self.table) and 0 <= x_pos + i < len(self.table[y_pos]) \
                    and self.table[y_pos + i][x_pos + i] == token:
                count += 1
                if count >= 4:
                    self.win = True
                    return
            else:
                break

        # Check diagonal top left to bottom right
        count = 0
        for i in range(4):
            if 0 <= y_pos - i < len(self.table) and 0 <= x_pos + i < len(self.table[y_pos]) \
                    and self.table[y_pos - i][x_pos + i] == token:
                count += 1
                if count >= 4:
                    self.win = True
                    return
            else:
                break

    def add_token(self, emoji):# assidinging each reaction a value so it would be easier to delete the whole reaction when a particlar column is full
        p2 = not self.p1
        if emoji == "1️⃣":
            j = 1
        elif emoji == "2️⃣":
            j = 2
        elif emoji == "3️⃣":
            j = 3
        elif emoji == "4️⃣":
            j = 4
        elif emoji == "5️⃣":
            j = 5
        elif emoji == "6️⃣":
            j = 6
        else:
            j = 7

        for i in range(0, 6):
            if self.table[5 - i][j] == "⚫":
                if self.p1:
                    self.table[5 - i][j] = "🔴"
                else:
                    self.table[5 - i][j] = "🟡"
                y_pos = 5 - i
                x_pos = j
                self.p1 = p2
                break
        else:
            return None

        self.check_win(x_pos, y_pos)
        self.check_draw()
        return j

    def reset(self):# resets the table and the other necessary variables
        self.table = [
            ["┃", "⚫", "⚫", "⚫", "⚫", "⚫", "⚫", "⚫", "┃"],
            ["┃", "⚫", "⚫", "⚫", "⚫", "⚫", "⚫", "⚫", "┃"],
            ["┃", "⚫", "⚫", "⚫", "⚫", "⚫", "⚫", "⚫", "┃"],
            ["┃", "⚫", "⚫", "⚫", "⚫", "⚫", "⚫", "⚫", "┃"],
            ["┃", "⚫", "⚫", "⚫", "⚫", "⚫", "⚫", "⚫", "┃"],
            ["┃", "⚫", "⚫", "⚫", "⚫", "⚫", "⚫", "⚫", "┃"]
        ]
        self.p1 = True
        self.win = False
        self.draw = False


    


client = commands.Bot(command_prefix='!', intents=discord.Intents.all())# creating bot
client.games = {}# creating a dictionary to store all of the current games


@client.event
async def on_ready():
    print("The bot is now ready")# checking to see if bot is working when it boots up.
    print("---------------------")


@client.command()
async def start(ctx):
    print("Embed command triggered")
    player1 = ctx.author
    game = Game(player1)
    embed = discord.Embed(title="Start", description=None, color=discord.Colour.random())
    embed.add_field(name='How to Play:', value='press the emojis to place down tokens on desired column. \n \n  Player 1 is the one who started command, player 2 is the one who clicked the "▶" emoji  \n \n Press ▶ to Play.', inline=False)
    msg = await ctx.send(embed=embed)
    client.games[msg.id] = game
    await msg.add_reaction("▶")# adding play emoji to start a match
    await msg.add_reaction("❌")# adding a cross emoji if player decides to not start a match
    


@client.event
async def on_reaction_add(reaction, user):# whenever a reaction is added:
    if user == client.user:# bot user can't reply to itself and create an infinte loop
        return

    msg = reaction.message
    
    if msg.id not in client.games:# game has ended 
        return

    game = client.games[msg.id]# putting into a disctionary, each message has a unique identifier; therfore perfect to make the key value so games aren't unexpectly interlinked to one and another.

    if user != game.player1:# this makes sure that a player can't play with themsleves and must play with another persoon
        if str(reaction.emoji) == "▶":
            await msg.remove_reaction("▶", user)
            await msg.clear_reaction("▶")
            table_string = "\n".join([" ".join(row) for row in game.table])
            embed = discord.Embed(title="Connect 4 Table", description=table_string, color=discord.Colour.random())
            game.player2 = user# player who cliked the play button is now player 2
            await msg.edit(embed=embed)
            await msg.add_reaction("1️⃣")
            await msg.add_reaction("2️⃣")
            await msg.add_reaction("3️⃣")
            await msg.add_reaction("4️⃣")
            await msg.add_reaction("5️⃣")
            await msg.add_reaction("6️⃣")
            await msg.add_reaction("7️⃣")
            await msg.add_reaction("❌")# adding in the emojis necessary to play the game

    if game.p1:# makes sure that only the user when it's their turn can make a move.
        player = game.player1
    else:
        player = game.player2
    if user == player:# therefore only the player's reaction matters and other people can't try to sabotage the game by clicking the reactions
        if str(reaction.emoji) in ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣"]:# if one of the columns have been clciked.
            await msg.remove_reaction(reaction.emoji, user)
            j = game.add_token(reaction.emoji)
            table_string = "\n".join([" ".join(row) for row in game.table])
            embed = discord.Embed(title="Connect 4 Table", description=table_string, color=discord.Colour.random())
            await msg.edit(embed=embed)

            if game.win:
                if game.p1:# that means that player2's turn just won therefore player 2 is winner
                    embed = discord.Embed(title="Connect 4 Table", description= game.player2.name +  "won!!!", color=discord.Colour.random())
                        
                    if game.player2.avatar:# if they have an profile picture, then display it alongside the winning message.
                        embed.set_image(url = game.player2.avatar.url)
                    await msg.edit(embed=embed)
                                    
                else:# that means that player1's turn just won therefore player 1 is winner
                    embed = discord.Embed(title="Connect 4 Table", description= game.player1.name +  "won!!!", color=discord.Colour.random())
                        
                    if game.player1.avatar:
                        embed.set_image(url = game.player1.avatar.url)
                    await msg.edit(embed=embed)


            if game.draw:# if game is drawn
                embed = discord.Embed(title="Connect 4 Table", description="Draw",
                                      color=discord.Colour.random())
                await msg.edit(embed=embed)

            if game.table[0][j] != "⚫":# if the column is full then remove the reaction emoji as it's not needed anymore for this game.
                await msg.clear_reaction(reaction.emoji)

    if user in [game.player1, game.player2] and str(reaction.emoji) == "❌":# therefore both players can clcik remove and it message will be deleted.
        game.reset()# resets everything
        await msg.delete()# deletes the message


client.run("BOT TOKEN GOES IN HERE")# token to connect bot to code
