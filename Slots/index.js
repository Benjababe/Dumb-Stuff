$(document).ready(() => {
    console.log("jQuery loaded");
    
    function Slot(elem, max, step, interval = 100) {
        this.elem = elem;
        this.max = max;
        this.step = step;
        this.speed = 80;
        
        this.spin;

        this.start = function() {
            this.speed = 50;
            setInterval(() => {
                if (this.speed < this.max) 
                    this.speed += this.step;
                else
                    this.speed = this.max;
            }, 250)
            this.spin = setInterval(() => {
                let cur = parseInt($(this.elem).css("background-position-y"));
                cur -= this.speed;
                $(this.elem).css("background-position-y", cur);
            }, interval)
        }
        
        this.stop = function() {
            clearInterval(this.spin);
            let cur = parseInt($(this.elem).css("background-position-y"));
            let rem = cur % 1746;
            console.log(rem);
            $(this.elem).css("background-position-y", cur + 1746 + (582 - rem));
        }
        
    }

    let slot = [];
    slot.push(new Slot("#slot1", 500, 50));
    slot.push(new Slot("#slot2", 500, 50));
    slot.push(new Slot("#slot3", 500, 50));

    $("#btnRoll").click(() => {
        slot[2].start();
        setTimeout(() => slot[1].start(), 200);
        setTimeout(() => slot[0].start(), 400);
    });
    
    $("#btnStop").click(() => {
        slot[2].stop();
        setTimeout(() => slot[1].stop(), 200);
        setTimeout(() => slot[0].stop(), 400);
    });
});

