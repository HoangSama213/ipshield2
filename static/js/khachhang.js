function toggleColumn(className) {
    document.querySelectorAll('.' + className).forEach(el => {
        el.style.display = (el.style.display === 'none') ? '' : 'none';
    });
}


document.addEventListener('DOMContentLoaded', function() {

    const cards_khtt = document.querySelectorAll(".card_khtt");
    const dots_khtt = document.querySelectorAll(".dot_khtt");
    const memberName_khtt = document.querySelector(".member-name_khtt");
    const memberRole_khtt = document.querySelector(".member-role_khtt");
    const upArrows_khtt = document.querySelectorAll(".nav-arrow_khtt.up_khtt");
    const downArrows_khtt = document.querySelectorAll(".nav-arrow_khtt.down_khtt");
    const playPauseBtn_khtt = document.getElementById("playPauseBtn_khtt");

    //  KIỂM TRA XEM CÓ ELEMENTS KHÔNG
    if (!cards_khtt.length || !memberName_khtt || !memberRole_khtt) {
        console.error('Không tìm thấy elements carousel!');
        return;
    }

    // KIỂM TRA XEM CÓ DỮ LIỆU KHÔNG
    if (typeof teamMembers_khtt === 'undefined' || !teamMembers_khtt.length) {
        console.error('Không có dữ liệu teamMembers_khtt!');
        return;
    }

    console.log('Carousel initialized with', teamMembers_khtt.length, 'members');

    let currentIndex_khtt = 0;
    let isAnimating_khtt = false;
    let autoplayInterval_khtt;
    let isPlaying_khtt = true;
    const AUTOPLAY_DELAY_khtt = 3000;

    function updateCarousel_khtt(newIndex){
        if(isAnimating_khtt) return;
        isAnimating_khtt=true;
        currentIndex_khtt=(newIndex+cards_khtt.length)%cards_khtt.length;

        cards_khtt.forEach((card,i)=>{
            const offset=(i-currentIndex_khtt+cards_khtt.length)%cards_khtt.length;
            card.classList.remove("center_khtt","up-1_khtt","up-2_khtt","down-1_khtt","down-2_khtt","hidden_khtt");
            if(offset===0) card.classList.add("center_khtt");
            else if(offset===1) card.classList.add("down-1_khtt");
            else if(offset===2) card.classList.add("down-2_khtt");
            else if(offset===cards_khtt.length-1) card.classList.add("up-1_khtt");
            else if(offset===cards_khtt.length-2) card.classList.add("up-2_khtt");
            else card.classList.add("hidden_khtt");
        });

        dots_khtt.forEach((dot,i)=>{
            dot.classList.toggle("active_khtt", i===currentIndex_khtt);
        });

        memberName_khtt.style.opacity="0";
        memberRole_khtt.style.opacity="0";

        setTimeout(()=>{
            memberName_khtt.textContent=teamMembers_khtt[currentIndex_khtt].name;
            memberRole_khtt.textContent=teamMembers_khtt[currentIndex_khtt].role;
            memberName_khtt.style.opacity="1";
            memberRole_khtt.style.opacity="1";
        },300);

        setTimeout(()=>{isAnimating_khtt=false;},800);
    }

    function startAutoplay_khtt(){
        if(autoplayInterval_khtt) clearInterval(autoplayInterval_khtt);
        autoplayInterval_khtt=setInterval(()=>{
            updateCarousel_khtt(currentIndex_khtt+1);
        },AUTOPLAY_DELAY_khtt);
        isPlaying_khtt=true;
        if(playPauseBtn_khtt) playPauseBtn_khtt.textContent="";
    }

    function stopAutoplay_khtt(){
        if(autoplayInterval_khtt){
            clearInterval(autoplayInterval_khtt);
            autoplayInterval_khtt=null;
        }
        isPlaying_khtt=false;
        if(playPauseBtn_khtt) playPauseBtn_khtt.textContent="";
    }

    function toggleAutoplay_khtt(){
        isPlaying_khtt?stopAutoplay_khtt():startAutoplay_khtt();
    }

    if(playPauseBtn_khtt) {
        playPauseBtn_khtt.addEventListener("click",toggleAutoplay_khtt);
    }

    upArrows_khtt.forEach(arrow=>{
        arrow.addEventListener("click",()=>{
            stopAutoplay_khtt();
            updateCarousel_khtt(currentIndex_khtt-1);
            setTimeout(startAutoplay_khtt,1000);
        });
    });

    downArrows_khtt.forEach(arrow=>{
        arrow.addEventListener("click",()=>{
            stopAutoplay_khtt();
            updateCarousel_khtt(currentIndex_khtt+1);
            setTimeout(startAutoplay_khtt,1000);
        });
    });

    dots_khtt.forEach((dot,i)=>{
        dot.addEventListener("click",()=>{
            stopAutoplay_khtt();
            updateCarousel_khtt(i);
            setTimeout(startAutoplay_khtt,1000);
        });
    });

    cards_khtt.forEach((card,i)=>{
        card.addEventListener("click",()=>{
            stopAutoplay_khtt();
            updateCarousel_khtt(i);
            setTimeout(startAutoplay_khtt,1000);
        });
    });

    document.addEventListener("keydown",(e)=>{
        if(e.key==="ArrowUp"){
            stopAutoplay_khtt();
            updateCarousel_khtt(currentIndex_khtt-1);
            setTimeout(startAutoplay_khtt,1000);
        } else if(e.key==="ArrowDown"){
            stopAutoplay_khtt();
            updateCarousel_khtt(currentIndex_khtt+1);
            setTimeout(startAutoplay_khtt,1000);
        }
    });

    let touchStartY_khtt=0, touchEndY_khtt=0;
    document.addEventListener("touchstart",(e)=>{
        touchStartY_khtt=e.changedTouches[0].screenY;
    });

    document.addEventListener("touchend",(e)=>{
        touchEndY_khtt=e.changedTouches[0].screenY;
        handleSwipe_khtt();
    });

    function handleSwipe_khtt(){
        const diff=touchStartY_khtt-touchEndY_khtt;
        if(Math.abs(diff)>50){
            stopAutoplay_khtt();
            diff>0?updateCarousel_khtt(currentIndex_khtt+1):updateCarousel_khtt(currentIndex_khtt-1);
            setTimeout(startAutoplay_khtt,100);
        }
    }

    function createScrollIndicator_khtt(){
        const indicator=document.createElement('div');
        indicator.className='scroll-indicator_khtt';
        indicator.innerHTML='';
        document.body.appendChild(indicator);
    }
    createScrollIndicator_khtt();


    updateCarousel_khtt(0);
    startAutoplay_khtt();

});