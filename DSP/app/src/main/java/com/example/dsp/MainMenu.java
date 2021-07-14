package com.example.dsp;

import androidx.appcompat.app.AppCompatActivity;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;

import com.example.dsp.R;
import com.example.dsp.ui.login.LoginActivity;


public class MainMenu extends AppCompatActivity {


    @Override
    protected void onCreate(Bundle savedInstanceState) {

        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main_menu);

        //import buttons
        final Button liveVideoFeedButton = findViewById(R.id.liveVideoFeed);
        final Button libraryButton = findViewById(R.id.videoLibrary);
        final Button alertsButton = findViewById(R.id.viewAlerts);
        final Button editButton = findViewById(R.id.editAlertPeriod);

        //Code for directing a user to diff page depending on what is selected
        liveVideoFeedButton.setOnClickListener(v -> {
            Intent intent = new Intent(MainMenu.this, liveVideoFeed.class);
            startActivity(intent);

        });
        libraryButton.setOnClickListener(v -> {
            Intent intent = new Intent(MainMenu.this, Library.class);
            startActivity(intent);
        });
        alertsButton.setOnClickListener(v -> {
            Intent intent = new Intent(MainMenu.this, Alerts.class);
            startActivity(intent);
        });
        editButton.setOnClickListener(v -> {
            Intent intent = new Intent(MainMenu.this, Edit.class);
            startActivity(intent);
        });





    }

}