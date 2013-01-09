!function(window) {
  /*
   * Hits an ajax endpoint on our server to check and see if the repos have been
   * retrieved yet. If they have, then we simply return from the function and reload the page.
   */
  function reloadIfReposReady() {
    $.getJSON('/ajax/repos-ready/', function(data) {
      if (data && data.repos_ready) {
        return window.location.reload();
      }
    });

    // just keep trying every second until we have repos
    setTimeout(arguments.callee, 1000);
  }

  // exports!
  window.PhillyPUGithub = {
    reloadIfReposReady: reloadIfReposReady
  };
}(this);
