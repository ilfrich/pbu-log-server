import React from "react"
import { util } from "quick-n-dirty-utils"
import LogViewer from "./LogViewer"
import { mixins } from "quick-n-dirty-react"

const style = {
    centerDiv: {
        ...mixins.center,
        width: "400px",
        padding: "30px",
        margin: "auto",
        background: "#eee",
        border: "1px solid #ccc",
        borderRadius: "8px",
    },
}


class LoginForm extends React.Component {

    constructor(props) {
        super(props)
        this.login = this.login.bind(this)
    }

    login() {
        const token = this.authToken.value
        this.props.submit(token)
    }

    render() {
        return (
            <div style={style.centerDiv}>
                <label style={mixins.label}>Auth Token</label>
                <input type="text" style={mixins.textInput} ref={el => { this.authToken = el }} />
                <div style={mixins.vSpacer(20)} />
                <div>
                    <button style={mixins.button} type="button" onClick={this.login}>Login</button>
                </div>
            </div>
        )
    }
}


class LoginWrapper extends React.Component {
    constructor(props) {
        super(props)

        this.state = {
            loggedIn: false,
            performingLogin: true,
            invalid: false,
        }

        this.setAuth =this.setAuth.bind(this)
        this.attemptLogin = this.attemptLogin.bind(this)
    }

    componentDidMount() {
        this.attemptLogin()
    }

    attemptLogin() {
        const header = util.getAuthJsonHeader()
        if (header.Authorization == null) {
            // no login attempt needed as we don't have an auth token
            this.setState({ performingLogin: false })
            return
        }
        
        fetch("/api/login-check", {
            headers: util.getAuthJsonHeader(),
        })
            .then(util.restHandler)
            .then(result => {
                // we are logged in and received available log levels
                this.props.setLogLevels(result.logLevels)
                this.setState({ loggedIn: true, invalid: false })
            })
            .catch(() => {
                // login failed
                console.error("Invalid auth token")
                this.setState({ invalid: true })
            })
            .finally(() => {
                this.setState({ performingLogin: false })
            })
    }

    setAuth(newAuthToken) {
        util.setAuthToken(newAuthToken)
        this.attemptLogin()
    }

    render() {
        return this.state.performingLogin === true ? (
            <>
                <div style={mixins.vSpacer(100)} />
                <div style={style.centerDiv}><em>Checking Login...</em></div>
            </>
        ) : (
            <>
                {this.state.loggedIn === true ? this.props.children : (
                    <div>
                        <div style={mixins.vSpacer(100)} />
                        {this.state.invalid === true ? (
                            <div style={mixins.center}>
                                <b style={mixins.red}>Invalid Auth Token</b>
                            </div>
                        ) : null}
                        <LoginForm submit={this.setAuth} />
                    </div>
                )}
            </>
        )
    }
}


class App extends React.Component {

    constructor(props) {
        super(props)

        this.state = {
            logLevels: [],
        }

        this.setLogLevels = this.setLogLevels.bind(this)
    }

    setLogLevels(logLevels) {
        this.setState({ logLevels })
    }

    render() {
        return (
            <LoginWrapper setLogLevels={this.setLogLevels}>
                <LogViewer logLevels={this.state.logLevels} />
            </LoginWrapper>
        )
    }
}

export default App
