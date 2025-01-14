#!/usr/bin/env nodejs

// readability http service
// install prerequisites with:
//    apt install nodejs yarnpkg
//    yarnpkg add @mozilla/readability
//
// start service with:
//   ./index.js
//
// usage:
//   curl https://www.example.com/original_link.html > page.html
//   curl -X POST -d @page.html http://localhost:8081?href=https://www.example.com/original_link.html
//
// This file is part of calo.news: A news platform
//
// Copyright (C) 2018-2023 Paolo Greppi
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Affero General Public License for more details.
// You should have received a copy of the GNU Affero General Public License
// along with this program (file LICENSE).
// If not, see <https://www.gnu.org/licenses/>.

var http = require("http");
var { Readability } = require('@mozilla/readability');
var { JSDOM } = require('jsdom');
var url = require('url');
var process = require('process')

process.on('SIGINT', () => {
  console.info("Interrupted")
  process.exit(0)
})

http.createServer(function (request, response) {
  if (request.method == 'POST') {
    var parsedUrl = url.parse(request.url, true);
    var queryAsObject = parsedUrl.query;
    var href = queryAsObject.href;
    console.log("POST " + JSON.stringify(queryAsObject));
    if (!href) {
      console.log('Supply url parameter');
      response.writeHead(500, 'Supply url parameter');
      response.end();
      return;
    }
    var body = '';
    request.setEncoding('utf-8');
    request.on('data', function (data) {
        body += data;
    });
    request.on('end', function () {
      var dom = new JSDOM(body, { url: href });
      var uri = url.parse(href);
      try {
        var reader = new Readability(dom.window.document);
        var readable = reader.parse();
        if (readable && 'title' in readable && 'content' in readable) {
          console.log(readable.title);
          response.writeHead(200, {'Content-Type': 'text/html; charset=utf-8'});
          response.end(readable.content);
        } else {
          console.log('Could not extract content');
          response.writeHead(500, 'Could not extract content');
          response.end();
          return;
        }
      }
      catch(err) {
        console.log('Readability threw');
        response.writeHead(501, 'Could not extract content');
        response.end();
        return;
      }
    });
  } else {
    response.writeHead(405, 'Only accepts POST');
    response.end();
    return;
  }
}).listen(8081, '0.0.0.0');

// Console will print the message
console.log('Server running at http://0.0.0.0:8081/');
