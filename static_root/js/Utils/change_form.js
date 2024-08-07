document.addEventListener('DOMContentLoaded', function() {
    console.log('DOMContentLoaded event fired');
    const inputTags = ['BUTTON', 'INPUT', 'SELECT', 'TEXTAREA'];

    function handleFormConstants() {
        const constantsElement = document.getElementById('django-admin-form-add-constants');
        console.log('constantsElement:', constantsElement);

        if (constantsElement) {
            const modelName = constantsElement.dataset.modelName;
            console.log('modelName:', modelName);
            
            if (modelName) {
                const form = document.getElementById(modelName + '_form');
                console.log('form:', form);

                if (form) {
                    for (const element of form.elements) {
                        // HTMLElement.offsetParent returns null when the element is not rendered.
                        if (inputTags.includes(element.tagName) && !element.disabled && element.offsetParent) {
                            console.log('Focusing element:', element);
                            element.focus();
                            break;
                        }
                    }
                } else {
                    console.error(`Form with ID "${modelName}_form" not found.`);
                }
            } else {
                console.error('Model name not found in dataset.');
            }
        } else {
            console.error('Element with ID "django-admin-form-add-constants" not found.');
        }
    }
    // Initial check
    handleFormConstants();

    // Delayed check in case the element is dynamically added later
    setTimeout(function() {
        console.log('Performing delayed check');
        handleFormConstants();
    }, 3000); // Adjust the delay as needed

    // Set up MutationObserver if element is not found initially
    if (!document.getElementById('django-admin-form-add-constants')) {
        console.log('Setting up MutationObserver');
        const observer = new MutationObserver(function(mutations, me) {
            const element = document.getElementById('django-admin-form-add-constants');
            if (element) {
                console.log('Element found by MutationObserver');
                handleFormConstants();
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