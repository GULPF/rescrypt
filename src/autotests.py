import org.transcrypt.autotester
import autotests_re

autoTester = org.transcrypt.autotester.AutoTester()

autoTester.run(autotests_re, 're_tests')
autoTester.done()
