'use strict';
var Alexa = require('alexa-sdk');
var APP_ID = undefined;  // can be replaced with your app ID if publishing
var facts = require('./facts');
var GET_FACT_MSG_EN = [
    "Here's your fact: ",
	"Your Fact is: ",
	"Following is your fact: ",
	"Below is your fact: ",
	"Fact is: "
]
// Test hooks - do not remove!
exports.GetFactMsg = GET_FACT_MSG_EN;
var APP_ID_TEST = "mochatest";  // used for mocha tests to prevent warning
// end Test hooks

/*
    TODO (Part 2) add messages needed for the additional intent
    TODO (Part 3) add reprompt messages as needed
*/
var languageStrings = {
    "en": {
        "translation": {
            "FACTS": facts.FACTS_EN,
            "SKILL_NAME": "My History Facts",  // OPTIONAL change this to a more descriptive name
            "GET_FACT_MESSAGE": GET_FACT_MSG_EN,
            "HELP_MESSAGE": "You can say tell me a fact, or, you can say exit... What can I help you with?",
            "HELP_REPROMPT": "What can I help you with?",
            "STOP_MESSAGE": "Goodbye!",
			"PROMPT_MESSAGE" : "WELCOME",
			"REPROMPT_MESSAGE" :"Please say tell me a fact to get a random fact",
			"REPROMPT_MESSAGE_YEAR" :"Please say tell me a fact followed by the year to get the fact from that year",
			"YEAR_NOT_FOUND": "Fact for this year is not available, here is another fact"
        }
    }
};

exports.handler = function (event, context, callback) {
    var alexa = Alexa.handler(event, context);
    alexa.APP_ID = APP_ID;
    // set a test appId if running the mocha local tests
    if (event.session.application.applicationId == "mochatest") {
        alexa.appId = APP_ID_TEST
    }
    // To enable string internationalization (i18n) features, set a resources object.
    alexa.resources = languageStrings;
    alexa.registerHandlers(handlers);
    alexa.execute();
};
	
/*
    TODO (Part 2) add an intent for specifying a fact by year named 'GetNewYearFactIntent'
    TODO (Part 2) provide a function for the new intent named 'GetYearFact' 
        that emits a randomized fact that includes the year requested by the user
        - if such a fact is not available, tell the user this and provide an alternative fact.
    TODO (Part 3) Keep the session open by providing the fact with :askWithCard instead of :tellWithCard
        - make sure the user knows that they need to respond
        - provide a reprompt that lets the user know how they can respond
    TODO (Part 3) Provide a randomized response for the GET_FACT_MESSAGE
        - add message to the array GET_FACT_MSG_EN
        - randomize this starting portion of the response for conversational variety
*/

var handlers = {
    'LaunchRequest': function () {
        this.emit('GetFact');
    },
    'GetNewFactIntent': function () {
        this.emit('GetFact');
    },
     'GetFact': function () {
        // Get a random fact from the facts list
        // Use this.t() to get corresponding language data
        var reprompt = this.t("REPROMPT_MESSAGE");
        var factArr = this.t('FACTS');
        var randomFact = randomPhrase(factArr);

        // Create speech output
        var speechOutput = randomPhrase(this.t("GET_FACT_MESSAGE")) + randomFact;
        this.emit(':askWithCard', speechOutput, reprompt, this.t("SKILL_NAME"), randomFact);
    },
    'GetNewYearFactIntent': function (intent) {
        this.emit('GetYearFact',intent);
    },
	 'GetYearFact': function (intent) {
        var year = this.event.request.intent.slots.FACT_YEAR.value;
        var fact = phraseByYear(facts.FACTS_EN,year);
		var reprompt = this.t("REPROMPT_MESSAGE_YEAR");
		if(fact.includes(year))
		{
		  var speechOutput = randomPhrase(this.t("GET_FACT_MESSAGE")) + fact ;
		  this.emit(':askWithCard', speechOutput,reprompt, year, fact);
		}
		else
		{
		  var speechOutput = randomPhrase(this.t("GET_FACT_MESSAGE")) + this.t("YEAR_NOT_FOUND") + fact ;
		  this.emit(':askWithCard', speechOutput,reprompt, year, fact);
		}   
    },
    'AMAZON.HelpIntent': function () {
        var speechOutput = this.t("HELP_MESSAGE");
        var reprompt = this.t("HELP_MESSAGE");
        this.emit(':ask', speechOutput, reprompt);
    },
    'AMAZON.CancelIntent': function () {
        this.emit(':tell', this.t("STOP_MESSAGE"));
    },
    'AMAZON.StopIntent': function () {
        this.emit(':tell', this.t("STOP_MESSAGE"));
    }
};

function randomPhrase(phraseArr) {
    // returns a random phrase
    // where phraseArr is an array of string phrases
    var i = 0;
    i = Math.floor(Math.random() * phraseArr.length);
    return (phraseArr[i]);
};

function phraseByYear(phraseArr,year) {
	var yearPhrase = null;
    for (var i = 0; i < phraseArr.length; i++) {
	  var yearFound = grepFourDigitNumber(phraseArr[i]);
	  if (yearFound==year) {
		return phraseArr[i]
	  }
	 }
	 return randomPhrase(phraseArr);
};

function grepFourDigitNumber(myString) {
        if (/\d{4}/.test(myString)) {
            return myString.match(/\d{4}/)[0];
        }
        else {
            return null
        }
    }
