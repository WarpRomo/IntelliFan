<p align="center">
<h1 align="center">IntelliFan</h1><br>
This project was created in collaboration between De Anza College & Infineon Technologies. The IntelliFan can automatically track a person and be controlled by gestures using the PSoC™ 6 AI Evaluation Kit and Raspberry Pi 4B. 
</p>
<p align="center">
<img src="https://github.com/user-attachments/assets/9ee6153f-9952-4676-a248-9d9905c61d2a"></img>
</p>

## Features
- Autotracking of people in front of the fan
- Gestures such as swiping left / right / up / down, to control the fan
- Web-app so user can control fan with their phone / laptop
- 3D models to house the fan and its components

<p align="center">
<img src="https://github.com/user-attachments/assets/c37bad27-6932-42db-a552-c7289d9f442d"></img>
</p>

## Person Tracking
Person tracking is done through the Raspberry Pi Camera 3 and YOLO X Nano on NCNN for optimized performance, alongside Byte Tracking to generate consistent IDs across frames to distinguish individuals.<br>https://github.com/Qengineering/YoloX-Tracking-ncnn-RPi_64-bit

<details>
<summary>Person Tracking</summary>
  <div align="center">
<video src='https://github.com/user-attachments/assets/445edbf3-a660-4a0f-84dc-7d0adf8acead'></video>
  </div>
</details>

<details>
<summary>Activate Person Tracking (Push)</summary>
  <div align="center">
<video src='https://github.com/user-attachments/assets/fc57ce63-2856-483f-b487-e727094a77c3'></video>
</details>

<details>
<summary>Change Person (Left)</summary>
  <div align="center">
<video src='https://github.com/user-attachments/assets/3c885a8b-cd1f-41d3-8687-49c4ffd364c1'></video>
</details>

<details>
<summary>Change Person (Right)</summary>
  <div align="center">
<video src='https://github.com/user-attachments/assets/9f6676e9-851d-4928-b4ec-0806f0841664'></video>
</details>

## Gesture Control
Gesture detection is done through radar using the BGT60TR13C sensor on the PSOC 6 Ai Evaluation Kit, which is then fed into DeepCraft's radar gesture model.<br>https://github.com/Infineon/mtb-example-ml-deepcraft-deploy-ready-model

<details>
<summary>Turn On (Up)</summary>
  <div align="center">
<video src='https://github.com/user-attachments/assets/34af48d3-125a-4831-8df4-11eee752b68b'></video>
</details>

<details>
<summary>Turn Off (Down)</summary>
  <div align="center">
<video src='https://github.com/user-attachments/assets/2ebcd7f2-937f-46ff-b61b-a43e5f5f2be0'></video>
</details>

<details>
<summary>Turn (Left)</summary>
  <div align="center">
<video src='https://github.com/user-attachments/assets/a7d5c35e-6d0c-4e75-ad39-ca346158de2c'></video>
</details>

<details>
<summary>Turn (Right)</summary>
  <div align="center">
<video src='https://github.com/user-attachments/assets/9fe7959b-e4da-4ded-935b-c23732035c80'></video>
</details>

## Web-app

The user can control the fan through their phone or laptop by connecting to the web server hosted over HTTP on the same WiFi.<br>Created by Warren and Zilu.
<details>
<summary>Web-app Demo</summary>
  <div align="center">
<video src='https://github.com/user-attachments/assets/1f611cf5-d45a-4a99-9636-2c5b928b5efd'></video>
</details>

## Components / Replication Cost

<table>
  
<tr>
<th align="left">
<small>Infineon PSoC™ 6 AI Evaluation Kit</small>
</th>
  
<th>
<small>$38.75</small>
</th>
</tr>
  
<tr>
<th align="left">
<small>Raspberry Pi 4 Model B (8GB RAM)</small>
</th>

<th>
<small>$39.99</small>
</th>
</tr>

<tr>
<th align="left">
<small>32GB microSD Card</small>
</th>

<th>
<small>$9.99</small>
</th>
</tr>

<tr>
<th align="left">
<small>Raspberry Pi Camera Module 3</small>
</th>

<th>
<small>$14.49</small>
</th>
</tr>

<tr>
<th align="left">
<small>PLA 3D-Printed Case and Housing</small>
</th>

<th>
<small>$6.99</small>
</th>
</tr>

<tr>
<th align="left">
<small>USB Type-C Cable</small>
</th>

<th>
<small>$4.99</small>
</th>
</tr>

<tr>
<th align="left">
<small>Servo Motor with Connecting Rod</small>
</th>

<th>
<small>$1.99</small>
</th>
</tr>

</table>




