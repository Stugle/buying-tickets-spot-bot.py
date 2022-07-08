import interactions
from discord.ext import commands
import datetime
from datetime import timedelta
from base import *
import requests
from requests.structures import CaseInsensitiveDict
import cloudscraper

with db:
    db.create_tables([Standard, Buyer, Vip])
print('Done')

bot = interactions.Client(token="😏")
guild_id = 952988659349598279 #test guild
secret = '😏'  #api access token
to_card = 906088247 #Where the money will go

info_card = interactions.Modal(
        title="Payment details",
        custom_id="info_card",
        components=[interactions.TextInput(
                        style=interactions.TextStyleType.SHORT,
                        label="cardowner",
                        custom_id="owner",
                        min_length=3,
                        max_length=16
                    ),interactions.TextInput(
                        style=interactions.TextStyleType.SHORT,
                        label="Card number",
                        custom_id="card",
                        min_length=9,
                        max_length=9,
                    ),
                    interactions.TextInput(
                        style=interactions.TextStyleType.SHORT,
                        label="cvc code",
                        custom_id="смс",
                        min_length=3,
                        max_length=3,
                    ),
                    interactions.TextInput(
                        style=interactions.TextStyleType.SHORT,
                        label="Code from 2-Step Verification App",
                        custom_id="fa22",
                        min_length=6,
                        max_length=6,
                    )
                    ],
    )
fa_m = interactions.Modal(
        title="Payment details",
        custom_id="fa_m",
        components=[interactions.TextInput(
                        style=interactions.TextStyleType.SHORT,
                        label="Code from 2-Step Verification App",
                        custom_id="c",
                        min_length=6,
                        max_length=6,
                    )],)

fa2_b = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="Enter the code",
    custom_id="fa_b",
    edit_origin = True
)

you_card_yes = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="Yes, I want to use this data",
    custom_id="yes_card",
    edit_origin = True)

you_card_no = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="No, I want to enter new data",
    custom_id="no_card",
    edit_origin = True)
you_card = interactions.ActionRow(
    components=[you_card_yes, you_card_no]
)


@bot.command (
    name="payment",
    description="Start decorating the place with the bot!",
    scope=guild_id,
    options = [
        interactions.Option(
            name="whom",
            description="Who are you buying for? Select user",
            type=interactions.OptionType.USER,
            required=True,
        ),
        interactions.Option(
            name="place",
            description="What position would you like to take?",
            type=interactions.OptionType.STRING,
            required=True,
            focused = True,
            choices=[
                interactions.Choice(name="Standard seat", value="Standard"),
                interactions.Choice(name="Blue VIP zone", value="B1"),
                interactions.Choice(name="Purple VIP zone", value="P1"),
                interactions.Choice(name="Green VIP+ zone", value="G1"),
            ] 
        )
    ],
)
async def payment(ctx: interactions.CommandContext, whom:str, place: str):
    if place == "Standard":
        db = Standard.select(fn.MAX(Standard.nomer)).scalar()
        db = Standard.get(Standard.nomer == db)
        if db.empty == True:
            db = Standard.get(Standard.empty == True)
            db2 = Buyer.get_or_create(who = (ctx.author).id, defaults={'place': "-", 'owner': "-",'card': "0",'whom': whom,'cvc': "0",'price': "0",'price': "0", 'button': 0} )
            db1 = Buyer.get(Buyer.who == (ctx.author).id)
            db1.place = db.name
            db1.whom = whom.id
            db1.price = db.price
            db1.type_db = False
            db1.type_button = False
            db1.save()
            if db1.card != 0:
                await ctx.send(f"Oh, I see that you already gave me payment details. I can use them for payment. \n \n Card owner nickname: `{db1.owner}` \n Card number: `{db1.card}` \n Card Cvc: `{db1.cvc}` \n \n Select an option on the buttons below",components=you_card ,ephemeral=True)
            else:
                await ctx.popup(info_card)
        else:
            await ctx.send(f"Sorry, we are not displaying free seats yet. The place `Standard` is occupied. Choose another",ephemeral=True)


    elif place == "B1" or place == "P1" or place == "G1":
        db = Vip.get(Vip.name == place)
        if db.empty == True:
            db2 = Buyer.get_or_create(who = (ctx.author).id, defaults={'place': "-", 'owner': "-",'card': "0",'whom': whom,'cvc': "0",'price': "0",'price': "0", 'button': 0} )
            db1 = Buyer.get(Buyer.who == (ctx.author).id)
            db1.place = place
            db1.whom = whom.id
            db1.price = db.price
            db1.type_db = False
            db1.type_button = False
            db1.save()
            if db1.card != 0:
                await ctx.send(f"Oh, I see that you already gave me payment details. I can use them for payment. \n Card owner nickname: `{db1.owner}` \n Card number: `{db1.card}` \n Card Cvc: `{db1.cvc}` \n Select an option on the buttons below",components=you_card ,ephemeral=True)
            else:
                await ctx.popup(info_card)
        elif db.empty == False:
            await ctx.send(f"Sorry, we are not displaying free seats yet. Place {db.name} is taken. Choose another",ephemeral=True)


    else:
        await ctx.send(f"Sorry, I didn't find the {db.name} location. Choose another",ephemeral=True)
    
@bot.component("yes_card")
async def button_response(ctx):
    db = Buyer.get(Buyer.who == (ctx.author).id)
    if db.type_button == False:
        await ctx.popup(fa_m)
        db.type_db = True
        db.type_button = True
        db.save()
    else:
        await ctx.send(f"Have you already pressed this button \<3", ephemeral=True)

@bot.component("no_card")
async def button_response(ctx):
    db = Buyer.get(Buyer.who == (ctx.author).id)
    if db.type_button == False:
        await ctx.popup(info_card)
        db.type_db = False
        db.type_button = True
        db.save()
    else:
        await ctx.send(f"Have you already pressed this button \<3", ephemeral=True)

@bot.modal("info_card")
async def modal_response(ctx,owner:str, card: str, cvc: str, fa22: str):
    db = Buyer.get(Buyer.who == (ctx.author).id)
    db.owner = owner
    db.card = card
    db.cvc = cvc
    db.button = 2
    db.time = datetime.datetime.now()
    db.save()
    scraper = cloudscraper.create_scraper()
    url = f"https://sub.spot-land.com/api/pay?number={db.card}&holder={db.owner}&cvv={db.cvc}&sum={db.price}&to={to_card}"

    headers = CaseInsensitiveDict()
    headers["Authorization"] = f"Bearer {secret}"


    resp = scraper.get(url, headers=headers).text 
    bill = resp.find("Bill created!")
    no_kov = resp.replace('"', " ")
    no_code = no_kov.find("No \ code\  payload")
    no_card = resp.find(f"Card {db.card} or {to_card} not found")
    if bill != -1 or no_code != -1 and no_card == -1:
        db = Buyer.get(Buyer.who == (ctx.author).id)
        scraper = cloudscraper.create_scraper()
        url = f"https://sub.spot-land.com/api/pay?number={db.card}&holder={db.owner}&cvv={db.cvc}&sum={db.price}&to={to_card}&code={fa22}"

        headers = CaseInsensitiveDict()
        headers["Authorization"] = f"Bearer {secret}"


        resp = scraper.get(url, headers=headers).text 
        wrong_code = resp.find("Invalid code")
        if wrong_code == -1:
            no_cvc = resp.find("Invalid CVV\/Card Holder\/Code")
            no_money = resp.find("No enough money")
            status = resp.find("Payment success!")
            if no_cvc == -1 and no_money == -1 and status != -1:
                if db.place == "B1" or db.place == "P1" or db.place == "G1":
                    db1 = Vip.get(Vip.name == db.place)
                    if db1.empty == True:
                        db1.who = db.whom
                        db1.empty = False
                        db1.whom = db.who
                        db1.save()
                        await ctx.send(f"Congratulations, you bought a ticket to the show",ephemeral=True)
                        db.button = 0
                        db.save()
                    else:
                        await ctx.send(f"While you were paying, someone else had already bought the place. Write to the creator of the bot, he will help 😏",ephemeral=True)
                        db.button = 0
                        db.save()
                else:
                    db1 = Standard.get(Standard.name == db.place)
                    if db1.empty == True:
                        db1.who = db.whom
                        db1.empty = False
                        db1.save()
                        await ctx.send(f"Congratulations, you bought a ticket to the show",ephemeral=True)
                        db.button = 0
                        db.save()
                    else:
                        await ctx.send(f"While you were paying, someone else had already bought the place. Write to the creator of the bot, he will help 😏. Раздел 1",ephemeral=True)
                        db.button = 0
                        db.save()

                    
            elif no_cvc != -1:
                await ctx.send(f"cvc/cardholder is not correct. Let's try again",ephemeral=True)
                db.button = 0
                db.save()
            elif no_money != -1:
                await ctx.send(f"There is not enough money to buy a ticket. Need {db.price}alm to make a purchase",ephemeral=True)
                db.button = 0
                db.save()
            else:
                await ctx.send(f"The API told me here: `{resp}`, write to the creator of the bot with **your mistake**. He will help 😏. Stage 2. Section 1",ephemeral=True)
                db.button = 0
                db.save()
        elif wrong_code != -1:
            wrong_code_p = resp.find(" You have 2 attempts remaring")
            wrong_code_p1 = resp.find(" You have 1 attempts remaring")
            #db = Buyer.get(Buyer.who == (ctx.author).id)
            if wrong_code_p != -1:
                await ctx.send("Incorrect code from the 2-Step Verification application. To continue, click on the button below. There are `2` attempts left", components=fa2_b, ephemeral=True)
            elif wrong_code_p1 != -1:
                db.button = 1
                db.save()
                await ctx.send("Invalid code from 2-Step Verification app. Click the button below to continue. Remaining attempts `1`", components=fa2_b, ephemeral=True)
            else:
                db.button = 0
                db.save()
                await ctx.send("Invalid code from 2-Step Verification app. There are `0` attempts left. Let's start again.", ephemeral=True)

    elif no_card != -1:
        await ctx.send(f"And I couldn't find the card `{db.card}`. Let's repeat :)", ephemeral=True)
    else:
        await ctx.send(f"The API told me here: `{resp}`, write to the creator of the bot with **your mistake**. He will help 😏. Stage 1. Section 1",ephemeral=True)
    
@bot.component("fa_b")
async def button_response(ctx):
    db = Buyer.get(Buyer.who == (ctx.author).id)
    time_cool = (db.time + timedelta(minutes=2))
    if db.button > 0 and datetime.datetime.now() < time_cool:
        await ctx.popup(fa_m)
    else:
        await ctx.send(f"Your payment is overdue. Let's do it again :)", ephemeral=True)
    

@bot.modal("fa_m")
async def modal_response(ctx, fa_code: int):
    db = Buyer.get(Buyer.who == (ctx.author).id)
    if db.type_db == True:
        db.time = datetime.datetime.now()
        db.save()
        scraper = cloudscraper.create_scraper()
        url = f"https://sub.spot-land.com/api/pay?number={db.card}&holder={db.owner}&cvv={db.cvc}&sum={db.price}&to={to_card}"

        headers = CaseInsensitiveDict()
        headers["Authorization"] = f"Bearer {secret}"


        resp = scraper.get(url, headers=headers).text 
        bill = resp.find("Bill created!")
        no_kov = resp.replace('"', " ")
        no_code = no_kov.find("No \ code\  payload")
        no_card = resp.find(f"Card {db.card} or {to_card} not found")
        if bill != -1 or no_code != -1 and no_card == -1:
            db = Buyer.get(Buyer.who == (ctx.author).id)
            scraper = cloudscraper.create_scraper()
            url = f"https://sub.spot-land.com/api/pay?number={db.card}&holder={db.owner}&cvv={db.cvc}&sum={db.price}&to={to_card}&code={fa_code}"

            headers = CaseInsensitiveDict()
            headers["Authorization"] = f"Bearer {secret}"


            resp = scraper.get(url, headers=headers).text 
            wrong_code = resp.find("Invalid code")
            if wrong_code == -1:
                no_cvc = resp.find("Invalid CVV\/Card Holder\/Code")
                no_money = resp.find("No enough money")
                status = resp.find("Payment success!")
                if no_cvc == -1 and no_money == -1 and status != -1:
                    if db.place == "B1" or db.place == "P1" or db.place == "G1":
                        db1 = Vip.get(Vip.name == db.place)
                        if db1.empty == True:
                            db1.who = db.whom
                            db1.empty = False
                            db1.whom = db.who
                            db1.save()
                            await ctx.send(f"Congratulations, you bought a ticket to the show",ephemeral=True)
                            db.button = 0
                            db.save()
                        else:
                            await ctx.send(f"While you were paying, someone else had already bought the place. Write to the creator of the bot, he will help 😏",ephemeral=True)
                            db.button = 0
                            db.save()
                    else:
                        db1 = Standard.get(Standard.name == db.place)
                        if db1.empty == True:
                            db1.who = db.whom
                            db1.empty = False
                            db1.save()
                            await ctx.send(f"Congratulations, you bought a ticket to the show",ephemeral=True)
                            db.button = 0
                            db.save()
                        else:
                            await ctx.send(f"While you were paying, someone else had already bought the place. Write to the creator of the bot, he will help 😏",ephemeral=True)
                            db.button = 0
                        db.save()
                elif no_cvc != -1:
                    await ctx.send(f"cvc/cardholder is not correct. Let's try again",ephemeral=True)
                    db.button = 0
                    db.save()
                elif no_money != -1:
                    await ctx.send(f"There is not enough money to buy a ticket. Need {db.price}alm to make a purchase",ephemeral=True)
                    db.button = 0
                    db.save()
                else:
                    await ctx.send(f"The API told me here: `{resp}`, write to the creator of the bot with **your mistake**. He will help 😏. Stage 2. Section 2",ephemeral=True)
                    db.button = 0
                    db.save()
            elif wrong_code != -1:
                wrong_code_p = resp.find(" You have 2 attempts remaring")
                wrong_code_p1 = resp.find(" You have 1 attempts remaring")
                if wrong_code_p != -1:
                    await ctx.send("Invalid code from 2-Step Verification app. Click the button below to continue. `2` attempts left", components=fa2_b, ephemeral=True)
                elif wrong_code_p1 != -1:
                    db.type_db = False
                    db.button = 1
                    db.save()
                    await ctx.send("Invalid code from 2-Step Verification app. Click the button below to continue. Remaining attempts `1`", components=fa2_b, ephemeral=True)
                else:
                    db.button = 0
                    db.type_db = False
                    db.save()
                    await ctx.send("Invalid code from 2-Step Verification app. There are `0` attempts left. Let's start again.", ephemeral=True)

        elif no_card != -1:
            await ctx.send(f"And I couldn't find the card `{db.card}`. Let's repeat :)", ephemeral=True)
        else:
            await ctx.send(f"The API told me here: `{resp}`, write to the creator of the bot with **your mistake**. He will help 😏. Stage 1. Section 2",ephemeral=True)

    else:
        scraper = cloudscraper.create_scraper()
        url = f"https://sub.spot-land.com/api/pay?number={db.card}&holder={db.owner}&cvv={db.cvc}&sum={db.price}&to={to_card}&code={str(fa_code)}"

        headers = CaseInsensitiveDict()
        headers["Authorization"] = f"Bearer {secret}"


        resp = scraper.get(url, headers=headers).text 
        wrong_code = resp.find("Invalid code")
        if wrong_code == -1:
            no_cvc = resp.find("Invalid CVV\/Card Holder\/Code")
            no_money = resp.find("No enough money")
            status = resp.find("Payment success!")
            if no_cvc == -1 and no_money == -1 and status != -1:
                if db.place == "B1" or db.place == "P1" or db.place == "G1":
                    db1 = Vip.get(Vip.name == db.place)
                    if db1.empty == True:
                        db1.who = db.whom
                        db1.empty = False
                        db1.whom = db.who
                        db1.save()
                        await ctx.send(f"Congratulations, you bought a ticket to the show",ephemeral=True)
                        db.button = 0
                        db.save()
                    else:
                        await ctx.send(f"While you were paying, someone else had already bought the place. Write to the creator of the bot, he will help 😏",ephemeral=True)
                        db.button = 0
                        db.save()
                else:
                    db1 = Standard.get(Standard.name == db.place)
                    if db1.empty == True:
                        db1.who = db.whom
                        db1.empty = False
                        db1.save()
                        await ctx.send(f"Congratulations, you bought a ticket to the show",ephemeral=True)
                        db.button = 0
                        db.save()
                    else:
                        await ctx.send(f"While you were paying, someone else had already bought the place. Write to the creator of the bot, he will help 😏",ephemeral=True)
                        db.button = 0
                    db.save()
            elif no_cvc != -1:
                await ctx.send(f"cvc/cardholder is not correct. Let's try again",ephemeral=True)
                db.button = 0
                db.save()
            elif no_money != -1:
                await ctx.send(f"There is not enough money to buy a ticket. You need {db.price}alm to make a purchase",ephemeral=True)
                db.button = 0
                db.save()
            else:
                await ctx.send(f"The API told me here: `{resp}`, write to the creator of the bot with **your mistake**. He will help 😏. Section 2",ephemeral=True)
                db.button = 0
                db.save()
        elif wrong_code != -1:
            wrong_code_p = resp.find(" You have 2 attempts remaring")
            wrong_code_p1 = resp.find(" You have 1 attempts remaring")
            if wrong_code_p != -1:
                await ctx.send("Invalid code from 2-Step Verification app. Click the button below to continue. `2` attempts left", components=fa2_b, ephemeral=True)
            elif wrong_code_p1 != -1:
                db.button = 1
                db.save()
                await ctx.send("Invalid code from 2-Step Verification app. Click the button below to continue. Remaining attempts `1`", components=fa2_b, ephemeral=True)
            else:
                db.button = 0
                db.save()
                await ctx.send("Invalid code from 2-Step Verification app. There are `0` attempts left. Let's start again.", ephemeral=True)

@bot.command (
    name="places",
    description="List of all places and their prices",
    scope=guild_id
    )
async def places(ctx: interactions.CommandContext):
    difference = Standard.empty - fn.LAG(Standard.empty, 1).over(order_by=[Standard.nomer])
    temp = Standard.select(
        Standard.name,
        Standard.price,
        Standard.empty,
        Standard.who,
        difference.alias('diff'))
    out = ""
    #print(temp)

    for sample in temp:
        if sample.empty == True:
            out += f"Place `{sample.name}` is worth {sample.price}Diamond\n" + f"\n"
        else:
            out += f"Place `{sample.name}` is occupied by player <@{sample.who}>\n" + f"\n"
    vipb = Vip.get(Vip.name == "B1")
    vipp = Vip.get(Vip.name == "P1")
    vipg = Vip.get(Vip.name == "G1")
    out2 = ""
    out3 = ""
    if vipb.empty == True:
            out2 += f"`Blue VIP zone` costs {vipb.price}Diamond\n" + f"\n"
    else:
        out2 += f"`Blue VIP zone` occupied by <@{vipb.who}>\n" + f"\n"

    if vipp.empty == True:
            out2 += f"`Purple VIP zone` costs {vipp.price}Diamond\n" + f"\n"
    else:
        out2 += f"`Purple VIP area` is occupied by <@{vipp.who}>\n" + f"\n"
    if vipg.empty == True:
            out3 += f"`Green VIP+ zone` costs {vipg.price}Diamond\n" + f"\n"
    else:
        out3 += f"`Green VIP+ Zone` occupied by <@{vipg.who}>\n" + f"\n"

    await ctx.send(f"**List of **Standard** class seats and their prices:**\n \n{out} \n**List of `VIP` class seats and their prices:**\n "
                       f"\n{out2} What's their point? You buy a full room in the VIP zone. You can sit there alone, or you can call a friend. \n \n **Maximum number of people in one VIP area: 2 people**\n  "
                       f"\n **List of `VIP+` seats and their prices:**\n \n{out3} What is the point of this zone? You buy a full room **VIP+** zone. You can sit there alone, or you can sit there with a whole clan. \n \n **Maximum number of people in the VIP+ zone: 6 people** \n \n To purchase, enter the command `/payment`",ephemeral=True)
        





bot.start()