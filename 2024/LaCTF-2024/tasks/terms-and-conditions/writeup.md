# terms-and-conditions

Challenge description:

![chall description](assets/chall.png)

When you access the link, you see the following page:

![initial page](assets/initial.png)

And if you try to click the `I Accept` button, he goes away

![button running](assets/button.gif)

The problem is, if you open the console the website will break:

![alt text](assets/broken.png)

But if you update the page with the console open, it doesn't break

![alt text](assets/notbroken.png)

analyzing the code, you will see the following code:

![alt text](assets/originalcode.png)

which you can change on the console for this:

```javascript
window.addEventListener("mousemove", function (e) {
    mx = 0;
    my = 0;
});
```

This will let you click the button, because it's not tracking your mouse anymore

![click](assets/click.gif)

`lactf{that_button_was_definitely_not_one_of_the_terms}`
