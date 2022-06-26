const {get_w, get_ajax_w} = require(`${__dirname}/fullpage`)
const fs = require('fs');
const express = require("express")
const bodyParser = require('body-parser');
const code = fs.readFileSync(`${__dirname}/slide.js`) + "\n";
const app = express()


String.prototype.format = function (args) {
    var result = this;
    if (arguments.length > 0) {
        if (arguments.length == 1 && typeof (args) == "object") {
            for (var key in args) {
                if (args[key] != undefined) {
                    var reg = new RegExp("({" + key + "})", "g");
                    result = result.replace(reg, args[key]);
                }
            }
        } else {
            for (var i = 0; i < arguments.length; i++) {
                if (arguments[i] != undefined) {
                    var reg = new RegExp("({)" + i + "(})", "g");
                    result = result.replace(reg, arguments[i]);
                }
            }
        }
    }
    return result;
}


app.use(bodyParser.urlencoded({extended: true}))

app.post("/api_fullpage/get_w", (req, res) => {
    let result = req.body;
    try {
        let w = get_w(...Object.values(result))
        res.send({
            "msg": "success",
            "data": w
        })
    } catch (e) {
        console.log(e);
        res.send({
            "msg": "error",
            "data": -1
        })
    }
})

app.post("/api_fullpage/get_ajax_w", (req, res) => {
    let result = req.body;
    try {
        let w = get_ajax_w(...Object.values(result))
        res.send({
            "msg": "success",
            "data": w
        })
    } catch (e) {
        console.log(e);
        res.send({
            "msg": "error",
            "data": -1
        })
    }
})

app.post("/api_slide/get_w", (req, res) => {
    let result = req.body;
    try {
        let w = eval(code + result.callback + '\nget_w("{gt}","{challenge}","{e}","{s}","{distance}","{passtimes}","{trace}")'.format({
            gt:result.gt,
            challenge:result.challenge,
            e:result.e,
            s:result.s,
            distance:result.distance,
            passtimes:result.passtimes,
            trace:result.track,
        }));
        res.send({
            "msg": "success",
            "data": w
        })
    } catch (e) {
        console.log(e);
        res.send({
            "msg": "error",
            "data": -1
        })
    }
})

app.listen(3000, function () {
    // console.log("监听端口3000成功")
})
