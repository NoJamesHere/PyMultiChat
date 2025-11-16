Currently I try to rewrite and split a few scripts to be more organized.

This is my first actual attempt at implementing classes inside a python project.

## Important Note: This repository is currently still WIP (Work-In-Progress). Please consider that this will be very unstable at runtime and might hold potential security risks and threats.

List of implementation ideas:
- Rooms + Topics ✔
- DM ✔
- Username Collision Handling
- Safe Disconnect 🔨

---
## Rooms
You can create rooms in two ways:
- **Default:** In the server's main script you can add default rooms that are always available.
- **Runtime:** A user is able to create a room using `/create <room>` and will join it upon creation.

Users can switch rooms using `/join <room>`


## DMs
You can direct message somebody via `/msg <user> <message>`.
When you receive or send a DM, the client will remember it, enabling quick replies: `/reply <message>`

---
