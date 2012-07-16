#!/usr/bin/env ruby
# encoding: utf-8

require "rubygems"
require "twitter"
require "mysql"
require "google_chart"
require "cgi"
require "erb"
require "cgi_helper"
include CGI_Helper
http_header


@term =''
cgi = CGI.new
if cgi.params['term']
  @term =cgi.params['term'].to_s
  con = Mysql.new 'localhost', 'root', '12345','tweets' # DB connection
  date = Time.new
  tweets_device = Hash.new

  current_date = date.strftime("%Y-%m-%d %H:%M:%S") #
  current_date = current_date.to_s
  regex = Regexp.new(/Twitter for (\w+)/) #Regular Expresion for extract user device 
  #insert Data in DB
  con.query("INSERT INTO terms(term,search_date)
              VALUES('#{@term}','#{current_date}')")
  
  ins = con.query("SELECT LAST_INSERT_ID() FROM terms ")

  last_insert_id =  ins.fetch_row.join("\s")
  last_insert_id = last_insert_id.to_i
  #Search @term in Twitter 10 recent terms 
	Twitter.search("#{@term} -rt", :rpp => 10, :result_type => "recent").results.map do |status| 
      source = status.source
      matchdata = regex.match(source)

      if matchdata
        device_t = matchdata[1]
      else
        device_t = "Other"
      end
      
      text = status.text
      puts text
      text.gsub("\"", "'")
      puts text
      #Insert Results for Twitter Search
      con.query("INSERT INTO twits (term_id,text,name_user,device)
               VALUES(\"#{last_insert_id}\",\"#{text}\",\"#{status.from_user}\",\"#{device_t}\")")	

      if tweets_device.has_key?(device_t)
        tweets_device[device_t] = tweets_device[device_t] + 1
      else
        tweets_device[device_t] = 1
      end

         
    end
  #Build Pie Chart for Users Devices 
GoogleChart::PieChart.new('500x050', "Tweets by Devices", false) do |pc|
        tweets_device.each do|source,count|
        pc.data source.to_s, count
  end

  html = File.read('searchtweets.html')

  erb = ERB.new(html)

  @out = "Data save in DB, for view results #{pc.to_url} in Pie Chart"
  puts erb.result

      
  con.close if con  
end  
end
