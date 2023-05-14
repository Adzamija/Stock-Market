import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    id=session["user_id"]
    db.execute("DELETE FROM ownership WHERE shares=0")
    user_dict = db.execute("SELECT * FROM users JOIN ownership ON ownership.user_id = users.id JOIN company ON company.id = ownership.company_id WHERE users.id=?", id)
    length_of_dict = len(user_dict)
    price = []
    total_list = []
    price_str = []
    # Getting price
    for n in range(0, length_of_dict):
        symbol = user_dict[n]["symbol"]
        current_price = lookup(symbol)
        c_price = float(current_price["price"])
        price.append(c_price)
        price_s=usd(c_price)
        price_str.append(price_s)
    total_list = []
    # Getting num of shares
    for n in range(0, length_of_dict):
        shares = user_dict[n]["shares"]
        total_list.append(shares)
    # Getting total
    total_prices=[]
    total_str = []
    for n in range(0, length_of_dict):
        result = price[n] * total_list[n]
        total_prices.append(result)
        total_str.append(usd(result))

    # Cash from DB
    cash = db.execute("SELECT cash FROM users WHERE id=?", id)
    cash = cash[0]["cash"]

    TOTAL = cash + sum(total_prices)
    TOTAL = usd(TOTAL)
    cash = usd(cash)

    return render_template("index.html", user_dict = user_dict, length = length_of_dict, price = price_str, total = total_str, cash = cash, TOTAL = TOTAL)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    id=session["user_id"]
    if request.method == "POST":
        user_symbol = request.form.get("symbol").upper()
        symbol_dict = lookup(user_symbol)
        if symbol_dict and request.form.get("shares"):

            try:
                number_of_shares = float(request.form.get("shares"))

            except ValueError:
                return apology("enter a valid NUMBER of shares", 400)

            if number_of_shares.is_integer() and number_of_shares > 0:
                # Name of the stock
                name = symbol_dict["name"]
                all_buyed_symbols = db.execute("SELECT symbol FROM company")
                # Checking is that symbol in DB or not
                symbols=[]

                # If is not, insert that symbol
                if not all_buyed_symbols:
                    db.execute("INSERT INTO company (company_name, symbol) VALUES (?,?)",name ,user_symbol)

                # If that symbol is in DB
                else:
                    # Getting all existing symbols
                    for n in range(0, len(all_buyed_symbols)):
                        symbols.append(all_buyed_symbols[n]["symbol"])
                    # If the user symbol is not in the company table DB, we are adding data about new company
                    if user_symbol not in symbols:
                        db.execute("INSERT INTO company (company_name, symbol) VALUES (?,?)",name ,user_symbol)


                # Stock price
                table_price = symbol_dict["price"]

                # Table number for SHARES
                num_for_table = int(request.form.get("shares"))

                # Full price [price*shares]
                price = number_of_shares * symbol_dict["price"]

                # Current balance for user
                balance_dict = db.execute("SELECT cash FROM users WHERE id=?", id)
                current_balance=float(balance_dict[0]["cash"])

                # New balance after potential buying
                new_balance = current_balance - price

                # Checking is user able to buy [if he/she had money]
                if new_balance >=0:

                    # Company ID from DB
                    company_id = db.execute("SELECT id FROM company WHERE symbol=?", user_symbol)
                    comp_id = company_id[0]["id"]

                    # All company_id for specific useer
                    id_dict = db.execute("SELECT company_id FROM ownership WHERE user_id=?", id)
                    print(id_dict)
                    # List of ids
                    ids=[]

                    # Getting all ids
                    for n in range(0, len(id_dict)):
                        ids.append(id_dict[n]["company_id"])
                    print(ids)


                    # Checking is that share purcshaced earlier or not
                    if comp_id in ids:
                        db_shares = db.execute("SELECT shares FROM ownership WHERE user_id=? AND company_id=?", id, comp_id)
                        print(db_shares)
                        current_shares = db_shares[0]["shares"] + num_for_table
                        db.execute("UPDATE ownership SET shares=? WHERE user_id=? AND company_id=?", current_shares, id, comp_id)
                    else:
                        # Inserting in ownership table
                        db.execute("INSERT INTO ownership(user_id, shares, company_id) VALUES(?, ?, ?)", id, num_for_table, comp_id)

                    # Taking the cash from users table
                    db.execute("UPDATE users SET cash=? WHERE id=?", new_balance, id)

                    #After buying "/" redirecting
                    user_dict = db.execute("SELECT * FROM users JOIN ownership ON ownership.user_id = users.id JOIN company ON company.id = ownership.company_id WHERE users.id=?", id)
                    length_of_dict = len(user_dict)
                    price = []
                    total_list = []
                    price_str = []
                    # Getting price
                    for n in range(0, length_of_dict):
                        symbol = user_dict[n]["symbol"]
                        current_price = lookup(symbol)
                        c_price = float(current_price["price"])
                        price.append(c_price)
                        price_s=usd(c_price)
                        price_str.append(price_s)
                    total_list = []
                    # Getting num of shares
                    for n in range(0, length_of_dict):
                        shares = user_dict[n]["shares"]
                        total_list.append(shares)
                    # Getting total
                    total_prices=[]
                    total_str = []
                    for n in range(0, length_of_dict):
                        result = price[n] * total_list[n]
                        total_prices.append(result)
                        total_str.append(usd(result))

                    # Cash from DB
                    cash = db.execute("SELECT cash FROM users WHERE id=?", id)
                    cash = cash[0]["cash"]

                    TOTAL = cash + sum(total_prices)
                    TOTAL = usd(TOTAL)
                    cash = usd(cash)
                    buy = True
                    return render_template("index.html", user_dict = user_dict, length = length_of_dict, price = price_str, total = total_str, cash = cash, TOTAL = TOTAL, buy = buy)

                else:
                    return apology("check inputs", 400)
            # If user don't have the cash
            else:
                return apology("check the inputs", 400)

        # For GET method
        else:
            return apology("check the inputs", 400)
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    return apology("TODO")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":

        #Ensure the symbol was submitted
        if not request.form.get("symbol"):
            return apology("enter the symbol", 400)
        # Getting symbol
        entered_symbol = request.form.get("symbol")
        symbol_dict = lookup(entered_symbol)
        if symbol_dict:
            price = symbol_dict["price"]
            price = usd(price)
            return render_template("quoted.html", response=symbol_dict, price = price)
        else:
            return apology("invalid symbol", 400)

    else:
        return render_template("quote.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    session.clear()

    if request.method == "POST":
        # Checking the username field
        if not request.form.get("username"):
            return apology("you must enter the username", 400)
        # Checking the password field
        elif not request.form.get("password"):
            return apology("you must enter the password", 400)
        elif not request.form.get("confirmation"):
            return apology("you must enter the confirmation password", 400)
        # Taking the inputs from USER
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        # Checking the length of username and password
        used_names = db.execute("SELECT username FROM users")
        for name in used_names:
            if username in name['username']:
                return apology("username is used, type other one", 400)
        if len(username) < 4 or len(password) < 8:
            return apology("your username must have more than 4 chars and password 8 and greater", 400)
        hash_password = generate_password_hash(password,method='pbkdf2:sha256', salt_length=8)
        if password == confirmation:
            # Getting hash password
            # hash_password = generate_password_hash(password,method='pbkdf2:sha256', salt_length=8)
            # Inserting values into DB
            db.execute("INSERT INTO users(username, hash) VALUES(?, ?)", username, hash_password)
            # After the user is registred, redirect to the /login page
            # ID
            id=db.execute("SELECT id FROM users WHERE username=?", username)
            session["user_id"] = id[0]["id"]
            message_successfull = True

            return render_template("indexed.html", message = message_successfull)
        else:
            return apology("conf", 400)

    else:
        return render_template("register.html")
    session.clear()


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    id=session["user_id"]
    user_symbols = db.execute("SELECT company.symbol FROM users JOIN ownership ON ownership.user_id= users.id JOIN company ON company.id=ownership.company_id WHERE users.id=?", id)
    if not user_symbols:
        current_symbol = False
        disable_button = False
    else:
        current_symbol = True
        disable_button = True
    if request.method == "POST":
        symbol = request.form.get("symbol").upper()
        num_of_shares = request.form.get("shares")
        # Checking the inputs from user
        if symbol not in user_symbols[0]["symbol"] or not symbol or not num_of_shares:
            return apology("Check the inputs", 400)
        else:
            # Taking the number of shares for specific user and symbol
            user_shares =db.execute("SELECT ownership.shares FROM users JOIN ownership ON ownership.user_id= users.id JOIN company ON company.id=ownership.company_id WHERE users.id=? AND company.symbol=?", id, symbol)
            # If number of shares that user want to sell is greater than number form DB, notify the user
            if int(num_of_shares) > int(user_shares[0]["shares"]):
                return apology("You don't have that number of shares", 400)
            else:
                comp_id =db.execute("SELECT ownership.company_id FROM ownership JOIN company ON company.id=ownership.company_id WHERE company.symbol=? AND ownership.user_id=?", symbol, id)
                print(comp_id)
                new_balance_of_shares = int(user_shares[0]["shares"]) - int(num_of_shares)
                db.execute("UPDATE ownership SET shares=? WHERE user_id=? AND company_id=?", new_balance_of_shares, id, comp_id[0]["company_id"])
                user_dict = db.execute("SELECT * FROM users JOIN ownership ON ownership.user_id = users.id JOIN company ON company.id = ownership.company_id WHERE users.id=?", id)
                length_of_dict = len(user_dict)
                price = []
                total_list = []
                price_str = []
                # Getting price
                for n in range(0, length_of_dict):
                    symbol = user_dict[n]["symbol"]
                    current_price = lookup(symbol)
                    c_price = float(current_price["price"])
                    price.append(c_price)
                    price_s=usd(c_price)
                    price_str.append(price_s)
                total_list = []
                # Getting num of shares
                for n in range(0, length_of_dict):
                    shares = user_dict[n]["shares"]
                    total_list.append(shares)
                # Getting total
                total_prices=[]
                total_str = []
                for n in range(0, length_of_dict):
                    result = price[n] * total_list[n]
                    total_prices.append(result)
                    total_str.append(usd(result))

                # Cash from DB
                cash = db.execute("SELECT cash FROM users WHERE id=?", id)
                cash = cash[0]["cash"]

                TOTAL = cash + sum(total_prices)
                TOTAL = usd(TOTAL)
                cash = usd(cash)
                current = True
                return render_template("index.html", user_dict = user_dict, length = length_of_dict, price = price_str, total = total_str, cash = cash, TOTAL = TOTAL, current = current)

    return render_template("sell.html", symbols=user_symbols, current=current_symbol, disable = disable_button)
