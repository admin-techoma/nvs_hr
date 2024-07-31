document.addEventListener('DOMContentLoaded', function() {
   
    
    const popupResponseElement = document.getElementById('django-admin-popup-response-constants');
    if (popupResponseElement) {
        handlePopupResponse(popupResponseElement);
    } else {
      
        
        const observer = new MutationObserver(function(mutations, me) {
            const element = document.getElementById('django-admin-popup-response-constants');
            if (element) {
                ;
                handlePopupResponse(element);
                me.disconnect(); // Stop observing
                return;
            }
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }
});

function handlePopupResponse(popupResponseElement) {
    try {
        const initData = JSON.parse(popupResponseElement.dataset.popupResponse);
      

        switch (initData.action) {
            case 'change':
                opener.dismissChangeRelatedObjectPopup(window, initData.value, initData.obj, initData.new_value);
                break;
            case 'delete':
                opener.dismissDeleteRelatedObjectPopup(window, initData.value);
                break;
            default:
                opener.dismissAddRelatedObjectPopup(window, initData.value, initData.obj);
                break;
        }
    } catch (error) {
        console.error('Error parsing popup response data:', error);
    }
}