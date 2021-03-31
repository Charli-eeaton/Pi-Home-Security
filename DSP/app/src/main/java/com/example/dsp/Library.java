package com.example.dsp;

import androidx.appcompat.app.AppCompatActivity;

import android.os.Bundle;
import android.webkit.WebView;

public class Library extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_library);

        //Set webview to media folder
        WebView activity_library = (WebView) findViewById(R.id.media);
        activity_library.loadUrl("http://192.168.0.29/library");
    }
}
