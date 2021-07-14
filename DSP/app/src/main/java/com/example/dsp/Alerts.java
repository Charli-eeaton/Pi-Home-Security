package com.example.dsp;

import androidx.appcompat.app.AppCompatActivity;

import android.os.Bundle;
import android.webkit.WebView;

public class Alerts extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_alerts);

        //Set "webview" to log file
        WebView activity_alerts = (WebView) findViewById(R.id.log);
        activity_alerts.loadUrl("http://raspberrypi.local/log.txt");

    }
}