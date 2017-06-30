 /*~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
           ______     ______     ______   __  __     __     ______
          /\  == \   /\  __ \   /\__  _\ /\ \/ /    /\ \   /\__  _\
          \ \  __<   \ \ \/\ \  \/_/\ \/ \ \  _"-.  \ \ \  \/_/\ \/
           \ \_____\  \ \_____\    \ \_\  \ \_\ \_\  \ \_\    \ \_\
            \/_____/   \/_____/     \/_/   \/_/\/_/   \/_/     \/_/


This is a sample Slack bot built with Botkit.

This bot demonstrates many of the core features of Botkit:

* Connect to Slack using the real time API
* Receive messages based on "spoken" patterns
* Reply to messages
* Use the conversation system to ask questions
* Use the built in storage system to store and retrieve information
  for a user.

# RUN THE BOT:

  Create a new app via the Slack Developer site:

    -> http://api.slack.com

  Get a Botkit Studio token from Botkit.ai:

    -> https://studio.botkit.ai/

  Run your bot from the command line:

    clientId=<MY SLACK TOKEN> clientSecret=<my client secret> PORT=<3000> studio_token=<MY BOTKIT STUDIO TOKEN> node bot.js

# USE THE BOT:

    Navigate to the built-in login page:

    https://<myhost.com>/login

    This will authenticate you with Slack.

    If successful, your bot will come online and greet you.


# EXTEND THE BOT:

  Botkit has many features for building cool and useful bots!

  Read all about it here:

    -> http://howdy.ai/botkit

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~*/
var http = require('http')
var request = require("request")
var env = require('node-env-file');
env(__dirname + '/.env');

if (!process.env.clientId || !process.env.clientSecret || !process.env.PORT) {
  console.log('Error: Specify clientId clientSecret and PORT in environment');
  usage_tip();
  process.exit(1);
}

var Botkit = require('botkit');
var debug = require('debug')('botkit:main');

var bot_options = {
    clientId: process.env.clientId,
    clientSecret: process.env.clientSecret,
    // debug: true,
    scopes: ['bot'],
    studio_token: process.env.studio_token,
    studio_command_uri: process.env.studio_command_uri,
    newsApiKey:process.env.newsApiKey
};

// Use a mongo database if specified, otherwise store in a JSON file local to the app.
// Mongo is automatically configured when deploying to Heroku
if (process.env.MONGO_URI) {
    var mongoStorage = require('botkit-storage-mongo')({mongoUri: process.env.MONGO_URI});
    bot_options.storage = mongoStorage;
} else {
    bot_options.json_file_store = __dirname + '/.data/db/'; // store user data in a simple JSON format
}

// Create the Botkit controller, which controls all instances of the bot.
var controller = Botkit.slackbot(bot_options);

var watsonMiddleware = require('botkit-middleware-watson')({
  username: '6c626788-d499-43d9-aecf-614ef6dd0083',
  password: '3nbbXhtD5KzG',
  workspace_id: '4060e206-08d8-4153-8c2a-b4ad2faa2371',
  version_date: '2016-09-20',
  minimum_confidence: 0.50, // (Optional) Default is 0.75
});

controller.middleware.receive.use(watsonMiddleware.receive);
controller.startTicking();
// Set up an Express-powered webserver to expose oauth and webhook endpoints
var webserver = require(__dirname + '/components/express_webserver.js')(controller);

// Set up a simple storage backend for keeping a record of customers
// who sign up for the app via the oauth
require(__dirname + '/components/user_registration.js')(controller);

// Send an onboarding message when a new team joins
require(__dirname + '/components/onboarding.js')(controller);

// no longer necessary since slack now supports the always on event bots
// // Set up a system to manage connections to Slack's RTM api
// // This will eventually be removed when Slack fixes support for bot presence
// var rtm_manager = require(__dirname + '/components/rtm_manager.js')(controller);
//
// // Reconnect all pre-registered bots
// rtm_manager.reconnect();

// Enable Dashbot.io plugin
require(__dirname + '/components/plugin_dashbot.js')(controller);


var normalizedPath = require("path").join(__dirname, "skills");
require("fs").readdirSync(normalizedPath).forEach(function(file) {
  require("./skills/" + file)(controller);
});

// This captures and evaluates any message sent to the bot as a DM
// or sent to the bot in the form "@bot message" and passes it to
// Botkit Studio to evaluate for trigger words and patterns.
// If a trigger is matched, the conversation will automatically fire!
// You can tie into the execution of the script using the functions
// controller.studio.before, controller.studio.after and controller.studio.validate

function getSentiment(symbol,cb){
  var url = "https://finsentiment.mybluemix.net/api/sentiment";
  request({
          url: url,
          json: true
        }, function (error, response, body) {
          if (!error && response.statusCode === 200) {
                cb(null,body);
          }else{
            console.log('error ' + error);
          }
      });
}

function getStockQuote(symbol,cb){
  var url = "https://finance.google.com/finance/info?q=NSE:" + symbol;
  request({
          url: url,
          json: true
        }, function (error, response, body) {
          if (!error && response.statusCode === 200) {
                cb(null,body);
          }else{
            console.log('error ' + error);
          }
      });
}

function getNews(cb){
  var result = "";
  var sources = [];
  
  var urlCategory = "https://newsapi.org/v1/sources?language=en&category=business";
  request({
          url: urlCategory,
          json: true
        }, function (error, response, body) {
          if (!error && response.statusCode === 200) {
                sources = body['sources'];
                sources.forEach(function(source){
                  var url = "https://newsapi.org/v1/articles?apiKey=" + process.env.newsApiKey + "&source=" + source['id'];
                  console.log('source URL ' + url);
                  request({
                      url: url,
                      json: true
                    }, function (error, response, body) {
                          if (!error && response.statusCode === 200) {
                              result += JSON.stringify(body);
                              cb(null,body)
                          }else{
                            console.log('error ' + error);
                          }
                      });
                });
          }else{
            console.log('error ' + error);
          }
      });
}


if (process.env.studio_token) {
    controller.hears(['.*'], ['direct_message', 'direct_mention', 'mention'], function(bot, message) {
        bot.reply(message, message.watsonData.output.text.join('\n'));
        var intent = message.watsonData.output.asking_for;
        var symbol = message.watsonData.output.symbol;
        console.log('intent is:' + intent);
        console.log('symbol is:' + symbol);
      console.log('intent is' + intent);
        if(intent === 'NEWS'){
            getNews( function(error, result){
                if(error){
                  bot.reply(message, 'Error in fetching news');
                }else{
                    var articles = result['articles'];
                    articles.forEach(function(article){
                    var newsTitle = JSON.stringify(article['title']);
                    if(symbol.toUpperCase() === 'ALL')
                        bot.reply(message, newsTitle);
                    else { 
                        newsTitle.split(" ").forEach(function(word){
                          if(word.indexOf(symbol) >= 0){
                            bot.reply(message, newsTitle);
                          }
                        });
                    }
                  });
                }
            });
          }else if(intent === 'STOCK_PRICE'){
            getStockQuote(symbol,function(error, result){
              if(error){
                  bot.reply(message, 'Error in fetching stock quote');
                }else{
                  var stockPrice = JSON.parse(result.substring(3,result.length))[0].l;
                  bot.reply(message, stockPrice);
                }
            });
          }else if(intent === 'SENTIMENT'){
            getSentiment(symbol,function(error, result){
              if(error){
                  bot.reply(message, 'Error in fetching sentiment data');
                }else{
                  var sentiments = result["results"];
                  for (var sentiment in sentiments) {                 
                    bot.reply(message, JSON.stringify(sentiment) + "-" + JSON.stringify(sentiments[sentiment]));
                  }
                }
            });
          }           
      });  //end hears
} else {
    console.log('~~~~~~~~~~');
    console.log('NOTE: Botkit Studio functionality has not been enabled');
    console.log('To enable, pass in a studio_token parameter with a token from https://studio.botkit.ai/');
}

function usage_tip() {
    console.log('~~~~~~~~~~');
    console.log('Botkit Starter Kit');
    console.log('Execute your bot application like this:');
    console.log('clientId=<MY SLACK CLIENT ID> clientSecret=<MY CLIENT SECRET> PORT=3000 studio_token=<MY BOTKIT STUDIO TOKEN> node bot.js');
    console.log('Get Slack app credentials here: https://api.slack.com/apps')
    console.log('Get a Botkit Studio token here: https://studio.botkit.ai/')
    console.log('~~~~~~~~~~');
}
