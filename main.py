# Flask
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy

# Twilio
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client

# Python module
import datetime
import time

# Own Files
from credentials import account_sid, auth_token

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'PlayersInfo'
    id = db.Column('id', db.Integer, primary_key=True)
    username = db.Column(db.String(200), nullable=False)
    password = db.Column(db.String(80), nullable=False)
    cgroup = db.Column(db.String(80), nullable=False)
    phoneNo = db.Column(db.String(80), nullable=False)
    points = db.Column(db.Integer, default=0)
    level = db.Column(db.String(80), default='user')
    date_created = db.Column(db.DateTime, default=datetime.datetime.now())

    def __init__(self, username, password, cgroup, phoneNo):
        self.username = username
        self.password = password
        self.cgroup = cgroup
        self.phoneNo = phoneNo


class Credentials:
    username = None
    password = None
    cellgroup = None
    phoneNo = None


# Global Variables
# system-used variables
client = Client(account_sid, auth_token)

# design-used variables
typeChallenges = ['repost', 'faceemoji', 'ratedesc', 'truthdare']
pointsChallenges = {
    'repost': 1,
    'faceemoji': 2,
    'ratedesc': 5,
    'truthdare': 7
}

egChallenge1 = 'https://scontent-lht6-1.cdninstagram.com/v/t51.2885-15/e35/89593053_303935520587348_8950539459587271008_n.jpg?_nc_ht=scontent-lht6-1.cdninstagram.com&_nc_cat=108&_nc_ohc=wmkSXhFBlbMAX8vw4ah&oh=7dba240a6f48ca003aae34084438fd35&oe=5EA98729'
egChallenge2 = 'https://scontent-lhr8-1.cdninstagram.com/v/t51.2885-15/e35/88204884_126986362197446_4152273722489357580_n.jpg?_nc_ht=scontent-lhr8-1.cdninstagram.com&_nc_cat=102&_nc_ohc=s7ePSTNCPiIAX9xpHzn&oh=c885b365968b2e1c2930a2e0bb8a13ae&oe=5EACD67E'
egChallenge3 = 'https://scontent-lhr8-1.cdninstagram.com/v/t51.2885-15/e35/83657105_188704399011850_372467535894358353_n.jpg?_nc_ht=scontent-lhr8-1.cdninstagram.com&_nc_cat=110&_nc_ohc=P2VFCqvnuZQAX9SIkDQ&oh=9a1390dc8c3e44ad02d6587ccec0f795&oe=5EAB115A'
egChallenge4 = 'https://scontent-lhr8-1.cdninstagram.com/v/t51.2885-15/e35/82262375_471360380196490_2995298621413961560_n.jpg?_nc_ht=scontent-lhr8-1.cdninstagram.com&_nc_cat=110&_nc_ohc=jQDui_qntDUAX-nnqtE&oh=faa46abb8458ae3eb719d632d91b45ea&oe=5EAB5CDE'


@app.route('/leaderboard', methods=['POST'])
def main():

    reset_Var()

    # Seting Variables
    incoming_msg = request.values.get('Body', '')
    num_media = int(request.values.get("NumMedia"))
    resp = MessagingResponse()
    msg = resp.message()

    currentDT = datetime.datetime.now().strftime("_%a, %d-%m-%Y, %I:%M:%S%p_")

    # Menu
    if incoming_msg == '0' or incoming_msg == '🔢' or incoming_msg.lower() == 'leaderboard help':
        msg.body(
            f"*Welcome to the #IFoundIt challenge, what would you like to do?*\n{currentDT}\n\n_*Reply with the number below(or emoji)*_\n\n1. Show the latest Leaderboard 📊️\n2. Register to Join 🤩\n3. Submit a Challenge 📲\n0. Main Menu 🔢")

    # Leaderboard
    elif incoming_msg == '1' or incoming_msg == '📊️':
        # msg.body(f'This will be available in a moment.')

        list_data = User.query.order_by(
            User.points).filter_by(level='user').all()
        list_data.reverse()

        listStringData = []

        for i in range(len(list_data)):
            temp_data = []

            temp_data.append('*' + str(list_data[i].username) + '*')
            temp_data.append('- _*' + str(list_data[i].points) + '*_')
            temp_data.append('_［' + str(list_data[i].cgroup) + '］_ ')

            if i == 0:
                indexNo = "🥇"
            elif i == 1:
                indexNo = "🥈"
            elif i == 2:
                indexNo = "🥉"
            else:
                indexNo = f'{i+1}.'

            temp_data.insert(0, indexNo)

            strTempData = ' '.join(temp_data)

            listStringData.append(strTempData)

        print("Leaderboard sent.")

        leaderboardStr = '\n'.join(listStringData)

        msg.body(
            f'#IFoundIt Leaderboard🏆\n{currentDT}\n\n{leaderboardStr}\n\nEnter 0 to return to Main Menu🔢')

        return str(resp)

    # Registration
    elif incoming_msg == '2' or incoming_msg == '🤩':
        msg.body(f'To register your name onto the Leaderboard, first you have to fill-in this registration form.📝\n_Just copy and paste this message._\n\nUsername: \nPassword: \nCell Group: \nPhone No.: ')

        return str(resp)

    elif 'To register your name onto the Leaderboard, first you have to fill-in this registration form.📝' in incoming_msg:
        registerUser = Credentials()
        registerUser.username = incoming_msg.split('\n')[3][10:]
        registerUser.password = incoming_msg.split('\n')[4][10:]
        registerUser.cellgroup = incoming_msg.split('\n')[5][12:].upper()
        registerUser.phoneNo = incoming_msg.split('\n')[6][11:]

        # formatting phoneNo
        if " " in registerUser.phoneNo:
            registerUser.phoneNo = registerUser.phoneNo.replace(
                " ", "")  # take out all whitespaces

        if '-' in registerUser.phoneNo:
            registerUser.phoneNo = registerUser.phoneNo.replace(
                "-", "")  # take out all the hyphens

        userObject = User(registerUser.username, registerUser.password,
                          registerUser.cellgroup, registerUser.phoneNo)

        if isValid_username(registerUser.username) == False:
            msg.body(
                f'The username *{registerUser.username}* has been taken.😕\nPlease use another username.')
            return str(resp)

        if isValid_cellgroup(registerUser.cellgroup) == False:
            msg.body(f'The Cell Group {registerUser.cellgroup} is not valid.😕\nPlease check that the format is according to this: _03J_ or _06S(A)_\n\nIf you are not sure about your Cell Group, please ask your friend for the valid CG Number.👥')
            return str(resp)

        # commit the registration to database
        try:
            db.session.add(userObject)
            db.session.commit()

            print("\nNew User Registed")
            print("Username: ", User.query.filter_by(
                username=registerUser.username).first().username)
            print("Password: ", User.query.filter_by(
                username=registerUser.username).first().password)
            print("Cell Group: ", User.query.filter_by(
                username=registerUser.username).first().cgroup)
            print("Phone No.: {}".format(User.query.filter_by(
                username=registerUser.username).first().phoneNo))

            msg.body(f'Congratulations!👏 You have created an account successfully.📲\nGo back to the main menu and submit a challenge\'s proof now!\n\nReply with a number(or emoji)\n\n0. Main Menu 🔢')
        except:
            msg.body(
                f'Theres an issue creating your account, please check that you have entered the information correctly.\n\nElse, contact system admin for assistance.\n_Kai Yang 016-3066883_\n_Andre 012-2005297_')

        return str(resp)

    # Submit a Challenge
    elif incoming_msg == '3' or incoming_msg == '📲':
        msg.body(f'*List of Points to be earned*😎\nREPOST - 1️⃣ point\nFACE EMOJI CHALLENGE - 2️⃣ points\nRATE/DESCIBE - 5️⃣ points\nTRUTH/DARE - 7️⃣ points\n\nTo Submit a challenge, tell me your username.')

        return str(resp)

    elif incoming_msg in [data.username for data in User.query.all()]:
        sendExamplesToUsers(incoming_msg)

    elif num_media:
        if ') (' in incoming_msg:
            incoming_msg = incoming_msg.lstrip('(').rstrip(')').split(') (')

            if len(incoming_msg) == 3:
                if validLogin(incoming_msg) == False:
                    msg.body(
                        "Your username or password is wrong.😲\nPlease try again.")
                    return str(resp)
                elif validType(incoming_msg) == False:
                    msg.body(
                        "Your type of challenge is wrong.😲\nRefer to the examples and try again.")
                    return str(resp)
                else:
                    media_url = request.values.get("MediaUrl0")

                    sendAdmin(
                        media_url, username=incoming_msg[0], type=incoming_msg[2])

                    print("A new submission is received.\n\nUsername: {}\nType: {}\nLink:\n{}".format(
                        incoming_msg[0], incoming_msg[2].upper(), media_url))

                    msg.body(
                        "Your challenge's proof had been submitted to be verified.📤\nYou will receive a notification soon.😉")
            else:
                msg.body(
                    "❌You have entered with the wrong format.\nPlease use the following format:\n\n_(Marcus Lee) (admin1234) (TruthDare)_")
        else:
            msg.body(
                "❌You have entered with the wrong format.\nPlease use the following format:\n\n_(Marcus Lee) (admin1234) (TruthDare)_")

        return str(resp)

    # For admin only
    elif 'i am admin' in incoming_msg.lower():
        msg.body(
            f'Prove yourself!😤 Login with an admin account using the following format.\n\nUsername: \nPassword: ')
        return str(resp)

    elif 'Prove yourself!😤 Login with an admin account using the following format.' in incoming_msg:
        adminUser = Credentials()
        adminUser.username = incoming_msg.split('\n')[2][10:]
        adminUser.password = incoming_msg.split('\n')[3][10:]

        admins = User.query.filter_by(level='admin')

        for admin in admins:
            if adminUser.username == admin.username and adminUser.password == admin.password:
                msg.body(f'Okay... You are really an admin.😢\nWelcome back!\nTo verify a user\'s submission, use the following template.\n\n*Verification Template*✅\nUsername: \nType: \nResult: \nComment: ')

    elif 'Okay... You are really an admin.😢\nWelcome back!\nTo verify a user\'s submission, use the following template.' in incoming_msg:
        verifyUser = Credentials()
        verifyUser.username = incoming_msg.split('\n')[5][10:]
        challengeType = incoming_msg.split('\n')[6][6:]
        result = incoming_msg.split('\n')[7][8:]
        adminComment = incoming_msg.split('\n')[8][9:]

        # take data of the user
        updateThis = User.query.filter_by(
            username=verifyUser.username).first()

        addPoints = 0

        if challengeType.lower() == 'repost':
            addPoints = pointsChallenges['repost']
        elif challengeType.lower() == 'faceemoji':
            addPoints = pointsChallenges['faceemoji']
        elif challengeType.lower() == 'ratedesc':
            addPoints = pointsChallenges['ratedesc']
        elif challengeType.lower() == 'truthdare':
            addPoints = pointsChallenges['truthdare']
        else:
            print("Error in the type of challenge. Please check your input.")
            msg.body(
                f'Seems like you have entered the wrong type of challenge🤔, please try again.')
            return str(resp)

        if result.lower() == 'pass' or result.lower() == 'verified':

            # add points to user
            updateThis.points += addPoints

            # commit db update
            db.session.commit()

            # send result to user
            client.messages.create(
                from_='whatsapp:+14155238886',
                body=f'Good News!📢\nYour challenge\'s proof had been verified.👏\nYou have earned *{addPoints} points*!\n\nBelow are the comments from our admin:\n_{adminComment}_',
                to=f'whatsapp:+6{updateThis.phoneNo}'
            )
        else:
            # send result to user
            client.messages.create(
                from_='whatsapp:+14155238886',
                body=f'I\'m sorry to inform that your challenge\'s proof does not pass the verification.😥\n\nBelow are the comments from our admin:\n{adminComment}',
                to=f'whatsapp:+6{updateThis.phoneNo}'
            )
    else:
        msg.body("Sorry I don't get what you said.😢")

    return str(resp)


def isValid_username(username):
    # check for username duplicates
    names = [data.username for data in User.query.all()]

    if username in names:
        return False

    return True


def isValid_cellgroup(cellgroup):
    # check for valid CG
    list_CG = ['01J', '08J', '06S(A)', '06S(B)',
               '07S', '03J', '09J', '02S']

    if cellgroup.upper() not in list_CG:
        return False

    return True


def sendExamplesToUsers(username):
    # Retrieve the phone number
    user = User.query.filter_by(username=username).first()

    exampleMediaURL = [egChallenge1, egChallenge2, egChallenge3, egChallenge4]

    for i in range(len(exampleMediaURL)):
        client.messages.create(
            from_='whatsapp:+14155238886',
            body=f'(Ah Gao) (pass123) ({typeChallenges[i]})',
            media_url=[f'{exampleMediaURL[i]}'],
            to=f'whatsapp:+6{user.phoneNo}'
        )
        time.sleep(1)

    time.sleep(3)

    client.messages.create(
        from_='whatsapp:+14155238886',
        body=f'Send me your challenge\'s proof(screenshot) according to the samples provided.\n\n💡Tips:\nreplace _Ah Gao_ with your username and _pass123_ with your password.\n*FOLLOW THE FORMAT!*',
        to=f'whatsapp:+6{user.phoneNo}'
    )


def validLogin(incoming_msg):
    # validate user login
    loginUser = Credentials()
    userCred = []

    loginUser.username = incoming_msg[0]
    loginUser.password = incoming_msg[1]

    userCred.append(loginUser.username)
    userCred.append(loginUser.password)

    listData = []

    for data in User.query.all():
        temp_data = []
        temp_data.append(data.username)
        temp_data.append(data.password)
        listData.append(temp_data)

    if userCred in listData:
        return True

    return False


def validType(incoming_msg):
    # validate the chalenge type
    challengeType = incoming_msg[2].lower()

    if challengeType in typeChallenges:
        return True

    return False


def sendAdmin(media_url, username, type):
    time.sleep(2)

    client.messages.create(
        from_='whatsapp:+14155238886',
        body=f'*Submission to be verified*\nUsername: {username}\nType: {type.upper()}',
        media_url=[f'{media_url}'],
        to=f'whatsapp:+60163066883'
    )


def reset_Var():
    pass


if __name__ == '__main__':
    app.run(debug=True)
