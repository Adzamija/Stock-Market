# Stock-Market
## Description
This project involves building a web application for managing a user's stock portfolio. The application will enable users to register for an account, buy and sell stocks.

## How To Use App

To run this project, you will need the following:

1. Python 3
2. Flask
3. Jinja2
4. SQLite3

## Specifications
1. Register

The register function allows a user to register for an account via a form. The user must input a username and password, and the application will store the hash of the user's password.

To implement the register function, complete the following steps:

Create a form with fields for the user's username and password.
Verify that the username is not blank and does not already exist in the users table.
Verify that the password is not blank and matches the confirmation.
Submit the form via POST to /register.
Insert the new user into the users table, storing the hash of the user's password.

2. Quote

The quote function allows a user to look up a stock's current price. The user must input a stock symbol, and the application will use the lookup function to retrieve the stock's current price.

To implement the quote function, complete the following steps:

Create a form with a field for the user's stock symbol.
Submit the form via POST to /quote.
Use the lookup function to retrieve the stock's current price.
Render the quoted.html template with the stock's symbol and price.

3. Buy

The buy function enables a user to buy stocks. The user must input a stock symbol and the number of shares to purchase. The application will verify that the user has enough funds to complete the purchase and insert a new transaction into the purchases table.

To implement the buy function, complete the following steps:

Create a form with fields for the user's stock symbol and the number of shares to purchase.
Verify that the user has enough funds to complete the purchase.
Insert a new transaction into the purchases table.

4. Index

The index function displays an HTML table summarizing the user's stock portfolio, including the number of shares owned, the current price of each stock, and the total value of each holding. The function also displays the user's current cash balance and a grand total of all holdings.

To implement the index function, complete the following steps:

Execute multiple SELECT statements to retrieve the user's holdings and current stock prices.
Render the index.html template with the user's holdings and cash balance.

5. Sell

The sell function enables a user to sell shares of a stock. The user must select the stock to sell and input the number of shares to sell. The application will verify that the user owns enough shares of the stock to complete the sale and insert a new transaction into the sales table.

To implement the sell function, complete the following steps:

Create a form with fields for the user's stock symbol and the number of shares to sell.
Verify that the user owns enough shares of the stock to complete the sale.
Insert a new transaction into the sales table.

## Contact

Any information, bugs or questions can be sent on the e-mail adress: adzamija@icloud.com
