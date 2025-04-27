PECKUS: **P**resence **E**nforcing **C**rypto-**K**ey **U**SB-**S**torage

# tl;dr
A circuitpython program that stores a bit of data (only a few kilobytes, presumably some crypto-key) in an internal storage (non-volatile-memory) of the microcontroller. When the microcontroller is attached to a USB port some presence-enforcing steps have to be completed (those can be configured during installation) for the microcontroller to expose its filesystem to the USB host - thus allowing (read-only) access to the data. To the USB host, it is just a (rather small) USB drive - but it doesn't expose its storage immediately, but only after the (configured) presence-enforcing checks have been completed by the user.

# Why?
You might want to store some crypto-key of yours on a portable device (because of the  portability benefits), but don't want to have it exposed when the device is lost or stolen. While the "standard" solution for this use-case is encryption, there are some drawbacks - let's take a quick look at this (for both hardware and software solutions):

1. Hardware-based encryption (a self-encrypting USB drive)

   **Usability: Unlocking**: Either the product has some form of a keyboard/keypad for you to type in the secret to unlock (decrypt) the drive or there is some sort of external authenticator device that performs this part

   **Usability: Relocking**: **If** the product even supports (automatic) re-locking of its storage, it's a bit risky in (usually employed) read-write access mode because the storage would suddenly just disappear - your operating system might not have already written all data to the device, possibly leading to file and/or filesystem corruptions. (The obvious solution to this is for the device to expose its storage as read-only, but whether that product even provides this configuration option is another question.)

   **Security: Trust**: It's probably a proprietary product - how much do you trust the manufacturer about not having implemented back-doors (passwords?), weak crypto or other things you wouldn't want?

   **Price**: These things tend to be somewhat expensive - and that's totally to be expected: those devices are rather niche-market products and they are also way more expensive to manufacture than plain old USB storage devices (by the way: those costs are __not__ due to the crypto-components but __much more__ due to all the things related to the user-interface, be it a keypad or fingerprint-reader or whatever).

2. Software-based encryption (a regular USB drive, but the data on it is encrypted by software running on the USB host)

   **Usability: Software**: TODO

   **Security: Unlocking**: TODO

   **Usability: Relocking**: TODO

So...did you find a product/solution that works for you (with respect to the aforementioned aspects)? Great! For me, for a very specific use-case (which I am not going to discuss - it is work related), there was no perfect (or even good) solution. So I started thinking about what I could implement myself; I quickly concluded for it to be a hardware based solution - and more specifically a microcontroller based solution (mostly due to cost aspects). With respect to software: I wanted to avoid any kind of software on endpoint devices (PC, Smartphone, ...) due to the complexity of such an endeavour; so the obvious solution was something that way essentially a USB disk drive - but with security related features implemented on the microcontroller. And thus was the question what software stack should I use? I opted against C/C++ with arduino/platformio because with circuitpython it should be a much faster development process (and I suspected that I wouldn't hit any limitiations implied by this choice, like performance or memory constraints). And in the end, it was the right choice (I "finished" my project and published it here) - although there were some roadbumps, I might write about them somewhere around here.

# Concept


# Security targets and assumptions


