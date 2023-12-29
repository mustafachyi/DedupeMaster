document.addEventListener('DOMContentLoaded', function() {
    const masterlist = document.getElementById('masterlist');
    const alert = document.getElementById('alert');
    const removed = document.getElementById('removed');
    const output = document.getElementById('output');
    const outputGroup = document.querySelector('.output-group');
    const kpblanks = document.getElementById('kpblanks');
    const caps = document.getElementById('caps');
    const sort = document.getElementById('sort');

    document.querySelector('.paste-btn').addEventListener('click', pasteInput);
    document.querySelector('.btn').addEventListener('click', doit);
    output.addEventListener('click', copyOutput);

    function pasteInput() {
        navigator.clipboard.readText()
        .then(text => {
            masterlist.value = text;
        })
        .catch(err => {
            console.error('Failed to read clipboard contents: ', err);
            alert.textContent = 'Failed to read clipboard contents.';
            alert.style.display = "block";
        });
    }

    function copyOutput() {
        output.select();
        document.execCommand('copy');
        output.style.animation = "borderPulse 2s";
        setTimeout(() => {
            output.style.animation = "";
        }, 2000);
    }

    function doit() {
        let txt = masterlist.value;
        if (!txt.trim()) {
            alert.style.display = "block";
            return;
        }
        alert.style.display = "none";
        txt = txt.replace(/>/g, "&gt;").replace(/</g, "&lt;");
        let masterarray = txt.split('\n');
        let dedupe = {};
        let editedArray = {};

        masterarray.forEach(item => {
            item = item.trimEnd().replace(/\t/g, '    ');
            if (!kpblanks.checked) {
                item = item.trimStart();
            } else if (item.match(/^ +/)) {
                let spc = item.match(/^ +/)[0].replace(/ /g, ' ');
                item = item.replace(/^\s+/, spc);
            }

            let ulc = caps.checked ? item.toLowerCase() : item;
            editedArray[ulc] = ulc;
            dedupe[ulc] = "0";
        });

        let uniques = Object.keys(dedupe).filter(key => editedArray[key] !== '');

        if (sort.checked) {
            uniques.sort((x, y) => {
                let a = x.toUpperCase();
                let b = y.toUpperCase();
                return a.localeCompare(b);
            });
        }

        let ulen = uniques.length;
        let thelist = uniques.join("\n");
        let rmvd = masterarray.length - ulen;
        removed.textContent = `${masterarray.length} original lines, ${rmvd} removed, ${ulen} remaining.`;
        output.textContent = thelist;
        outputGroup.style.display = "block";
    }
});