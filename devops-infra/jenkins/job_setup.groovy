import jenkins.model.*
import org.jenkinsci.plugins.workflow.job.WorkflowJob
import org.jenkinsci.plugins.workflow.cps.CpsScmFlowDefinition
import hudson.plugins.git.GitSCM
import hudson.plugins.git.UserRemoteConfig
import hudson.plugins.git.BranchSpec
import hudson.triggers.SCMTrigger
import java.util.logging.Logger

Logger logger = Logger.getLogger("job-setup-script")
logger.info("Starting DevSecOps job setup...")

try {
    def jobName = "DevSecOps-Pipeline"
    def jenkins = Jenkins.instance
    def job = jenkins.getItem(jobName)

    if (job == null) {
        logger.info("Job '${jobName}' does not exist. Creating...")
        job = jenkins.createProject(WorkflowJob.class, jobName)
        job.save()
    } else {
        logger.info("Job '${jobName}' already exists. Updating...")
    }

    // Define SCM (Git)
    def scm = new GitSCM(
        [new UserRemoteConfig("https://github.com/zalmanovmaxim-alt/devsecops-final-project.git", null, null, null)],
        [new BranchSpec("*/main")],
        false, [], null, null, []
    )

    // Set Pipeline Definition to use Jenkinsfile from SCM
    def flowDefinition = new CpsScmFlowDefinition(scm, "Jenkinsfile")
    flowDefinition.setLightweight(true) // Lightweight checkout
    job.setDefinition(flowDefinition)

    // Add SCM Poll Trigger (Every 5 minutes)
    // job.addTrigger(new SCMTrigger("H/5 * * * *")) // Optional, can enable if desired

    job.save()
    logger.info("DevSecOps job setup completed successfully.")

} catch (Exception e) {
    logger.severe("FAILED to set up DevSecOps job: " + e.getMessage())
    e.printStackTrace()
    // We swallow the exception so Jenkins doesn't crash during startup
}
