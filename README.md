# 🔐 Secure Chatting System (Pyhton + Flask) 
A web-based Secure chatting system built using Pyton + Flask that allows users to communicate in real-time with CHAOS encryption.

## 📌 Overview

This project is a **secure communication platform** developed using:

- Python (Flask)
- HTML, CSS, JavaScript
- Client-Server Architecture

It enables users to send and receive messages through a web interface with encryption and decryption.

## 📌 Purpose

This project demonstrates a simple secure communication system.

It is based on a scenario where one person sends messages to team members in different locations. Since communication may happen over unsafe networks, messages need to be protected so that no unauthorized person can read them.


## 🧠 Conceptual Scenario

- A central user sends instructions to multiple team members.
- Each message is encrypted using shared secret values (chaotic parameters).
- These values act like a secret key.
- Only users who know these values can decrypt and read the message.

Similarly:
- Team members send replies using the same method.
- The central user can decrypt those messages using the same values.


## 🔐 Security Approach

- Messages are encrypted before sending.
- Encrypted messages cannot be understood without the correct values.
- The same values are required for decryption.
- Even if someone intercepts the message, they cannot read it without the secret parameters.


## ⚠️ Important Note

This project is created for learning and demonstration purposes.

It shows how secure communication can be implemented using chaotic systems, but it is not as strong as real-world encryption methods like AES or RSA.


## ⚙️ Features

- Real-time chat interface
- Flask-based backend server
- Clean and responsive UI
- Message handling system
- Encryption for secure communication
- Lightweight and easy to run


## 🧠 How It Works

1. Before run create a newfolder in the clone repo with name "templates" and copy "admin.html, dashboard.html, signupp.html and login.html" to this folder.
2. Run app.py
3. Copy flask server link
4. Opens the web browser
5. Paste link and Connects to Flask server
6. Boom you got it run and now explore
7. signup and login
8. To Sends messages search user name of user to send message and he will add into your dashboard like whatsapp
9. Server processes and forwards messages
10. Messages are encrypted before sending


## ▶️ How to Run

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/secure-chat-system.git
cd secure-chat-system
